import time
import json

def calculate_mac(pattern, filter_data):
    score = 0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score

def measure_mac(pattern, filter_data, repeats=10):
    start = time.perf_counter()

    for _ in range(repeats):
        calculate_mac(pattern, filter_data)

    end = time.perf_counter()

    average_ms = (end - start) * 1000 / repeats

    return average_ms


def validate_matrix(matrix, size):
    if not isinstance(matrix, list) or len(matrix) != size:
        return False

    for row in matrix:
        if not isinstance(row, list) or len(row) != size:
            return False

        for value in row:
            if type(value) not in (int, float):
                return False

    return True


def compare_performance():
    print("\n=== 크기별 MAC 성능 비교 ===")

    for size in [3, 5, 13, 25]:
        pattern = [[1] * size for _ in range(size)]
        filter_data = [[1] * size for _ in range(size)]

        average_ms = measure_mac(pattern, filter_data)

        print(f"{size}x{size} | 곱셈 {size ** 2}회 | 평균 {average_ms:.6f} ms")


def input_matrix(name):
    matrix = []

    print(f"\n{name} (3줄 입력, 공백 구분)")

    while len(matrix) < 3:
        row = input(f"{len(matrix) + 1}번째 줄: ").split()

        if len(row) != 3:
            print("입력 형식 오류: 숫자 3개를 입력하세요.")
            continue

        try:
            numbers = [float(value) for value in row]
            matrix.append(numbers)
        except ValueError:
            print("입력 오류: 숫자만 입력하세요.")

    return matrix


print("=== Mini NPU Simulator ===")
print()
print("[모드 선택]")
print("1. 사용자 입력 (3x3)")
print("2. data.json 분석")

choice = input("선택 (1 또는 2): ").strip()

if choice == "1":
    print("\n사용자 입력 모드를 선택했습니다.")

    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")

    print("\n필터 저장 완료!")

    pattern = input_matrix("입력 패턴")

    score_a = calculate_mac(pattern, filter_a)
    score_b = calculate_mac(pattern, filter_b)

    print("\n=== MAC 결과 ===")
    print("A 점수:", score_a)
    print("B 점수:", score_b)
    print("MAC 곱셈 횟수:", 3 ** 2)
    
    time_a = measure_mac(pattern, filter_a)
    time_b = measure_mac(pattern, filter_b)

    print("A 평균 연산 시간:", f"{time_a:.6f}", "ms")
    print("B 평균 연산 시간:", f"{time_b:.6f}", "ms")

   
    epsilon = 1e-9

    if abs(score_a - score_b) < epsilon:
        print("판정: UNDECIDED")
    elif score_a > score_b:
        print("판정: A")
    else:
        print("판정: B")

elif choice == "2":
    print("\ndata.json 분석 모드입니다.")

    
    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        print("오류: data.json 파일을 찾을 수 없습니다.")
        raise SystemExit
    except json.JSONDecodeError:
        print("오류: data.json 파일의 JSON 형식이 올바르지 않습니다.")
        raise SystemExit


   
    if not isinstance(data, dict):
        print("오류: JSON 데이터는 객체 형태여야 합니다.")
        raise SystemExit

    if "filters" not in data or "patterns" not in data:
        print("오류: filters 또는 patterns 항목이 없습니다.")
        raise SystemExit

    filters = data["filters"]
    patterns = data["patterns"]


    print("JSON 파일 불러오기 성공!")
    print("필터 크기:", list(filters.keys()))
    print("패턴 개수:", len(patterns))


    print("\n=== 패턴 목록 ===")
    
    pass_count = 0
    fail_count = 0
    failed_patterns = []
   
    for pattern_name, pattern_info in patterns.items():
        size = pattern_name.split("_")[1]
        filter_key = "size_" + size

        filter_cross = filters[filter_key]["cross"]
        filter_x = filters[filter_key]["x"]

        pattern = pattern_info["input"]

        if not (
            validate_matrix(pattern, int(size))
            and validate_matrix(filter_cross, int(size))
            and validate_matrix(filter_x, int(size))
        ):
            print("오류: 행렬 크기 또는 데이터 형식이 올바르지 않습니다.")
            print("문제가 있는 패턴:", pattern_name)
            raise SystemExit

        score_cross = calculate_mac(pattern, filter_cross)

        score_x = calculate_mac(pattern, filter_x)

        time_cross = measure_mac(pattern, filter_cross)
        time_x = measure_mac(pattern, filter_x)


        epsilon = 1e-9

        if abs(score_cross - score_x) < epsilon:
            prediction = "UNDECIDED"
        elif score_cross > score_x:
            prediction = "Cross"
        else:
            prediction = "X"


        print("패턴 이름:", pattern_name)
        print("필터 크기:", size + "x" + size)
        print("MAC 곱셈 횟수:", int(size) ** 2)
        print("기대 정답:", pattern_info["expected"])
        print("십자가 점수:", score_cross)
        print("X 점수:", score_x)
        print("십자가 평균 시간:", f"{time_cross:.6f}", "ms")
        print("X 평균 시간:", f"{time_x:.6f}", "ms")
        

        expected = pattern_info["expected"]

        if expected == "+":
            expected = "Cross"
        elif expected.lower() == "x":
            expected = "X"

       
        if prediction == expected:
            result = "PASS"
            pass_count += 1
        else:
            result = "FAIL"
            fail_count += 1
            failed_patterns.append(pattern_name)


        print("최종 판정:", prediction)
        print("기대 정답(변환):", expected)
        print("검증 결과:", result)

        print("십자가 필터 행 개수:", len(filter_cross))
        print("X 필터 행 개수:", len(filter_x))
        print("--------------------")


    print("\n=== 전체 분석 결과 ===")
    print("전체 테스트:", len(patterns))
    print("PASS:", pass_count)
    print("FAIL:", fail_count)
    print("실패한 패턴:", failed_patterns)
    compare_performance()

else:
    print("잘못된 선택입니다. 1 또는 2를 입력하세요.")
