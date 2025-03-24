import os
import json
import base64
import zlib
from battle_report import generate_battle_report
from app.services.langchain_service import LangChainService

# 현재 실행 폴더 경로 가져오기
current_folder = os.getcwd()
json_file_path = os.path.join(current_folder, "test_lf.json")

# JSON 데이터를 재귀적으로 순회하며 출력하는 함수
def print_json_recursively(data, indent=0):
    indent_str = "  " * indent
    
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                print(f"{indent_str}{key}:")
                print_json_recursively(value, indent + 1)
            else:
                print(f"{indent_str}{key}: {value}")
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                print(f"{indent_str}[{i}]:")
                print_json_recursively(item, indent + 1)
            else:
                print(f"{indent_str}[{i}]: {item}")
    else:
        print(f"{indent_str}{data}")

# JSON 파일 읽기 및 로드
def load_json(file_path):
    if not os.path.exists(file_path):
        print(f"파일이 존재하지 않습니다: {file_path}")
        return None

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
    except json.JSONDecodeError as e:
        print(f"JSON 디코딩 오류: {e}")
        return None

# Base64 디코딩 후 zlib 압축 해제
def decode64_and_decompress(encoded_data):
    try:
        # Base64 디코딩
        decoded_bytes = base64.b64decode(encoded_data)
        # zlib 압축 해제
        decompressed_data = zlib.decompress(decoded_bytes).decode("utf-8")
        return decompressed_data
    except (base64.binascii.Error, zlib.error, UnicodeDecodeError) as e:
        print(f"디코딩/압축 해제 오류: {e}")
        return None
    
# JSON 데이터에서 특정 헤더와 키를 사용하여 데이터 추출 및 처리
def process_json_data(json_data, header, key):
    if not json_data or header not in json_data["_source"]:
        print(f"헤더 '{header}'를 찾을 수 없습니다.")
        return None
    
    if key not in json_data["_source"][header]:
        print(f"키 '{key}'를 찾을 수 없습니다.")
        return None
    
    base64_encoded = json_data["_source"][header][key]
    
    decompressed_data = decode64_and_decompress(base64_encoded)
    if not decompressed_data:
        return None
    
    try:
        parsed_data = json.loads(decompressed_data)
        return parsed_data
    except json.JSONDecodeError as e:
        print(f"JSON 파싱 오류: {e}")
        return None

# 전투 리포트 생성 및 저장 함수
def create_battle_report(json_data=None, header=None, key=None, report_type=None, output_filename=None):

    # 필수 인자 유효성 검사 (한 줄로 간소화)
    if None in (json_data, header, key, report_type):
        print(f"오류: 필수 인자가 누락되었습니다. (json_data: {json_data is not None}, header: {header is not None}, key: {key is not None}, report_type: {report_type is not None})")
        return None
    
    # 데이터 처리
    processed_data = process_json_data(json_data, header, key)
    if not processed_data:
        print("데이터 처리에 실패했습니다.")
        return None
    
    # 전투 리포트 생성
    battle_report = generate_battle_report(processed_data, report_type)

    if output_filename is not None:
        try:
            # reports 폴더 없으면 생성
            reports_folder = os.path.join(current_folder, "reports")
            if not os.path.exists(reports_folder):
                os.makedirs(reports_folder)

            report_file_path = os.path.join(reports_folder, output_filename)

            with open(report_file_path, "w", encoding="utf-8") as report_file:
                report_file.write(battle_report)
            print(f"\n전투 리포트(타입: {report_type}, 파일명: {output_filename})가 {report_file_path}에 저장되었습니다.")
        except Exception as e:
            print(f"리포트 저장 중 오류 발생: {e}")
    
    return battle_report

# 메인 실행 코드
def main():
    json_data = load_json(json_file_path)
    if not json_data:
        print("JSON 데이터를 로드할 수 없습니다.")
        return
    
    # 전투 리포트 생성 및 저장 (minimal, regular)
    # user_report_minimal = create_battle_report( json_data, "result_info", "user_record_minimal", "minimal", "user_report_minimal.txt" )
    # verify_report_minimal = create_battle_report( json_data, "result_info", "verify_record_minimal", "minimal", "verify_report_minimal.txt" )

    user_report_regular = create_battle_report( json_data, "result_info", "user_record_history", "regular", "user_report_regular.txt" )
    verify_report_regular = create_battle_report( json_data, "result_info", "verify_record_history", "regular", "verify_report_regular.txt" )

    # langchain_test_service = LangChainService()
    # analysis1 = langchain_test_service.process_analyze(user_report_regular,verify_report_regular)
    # analysis2 = langchain_test_service.process_analyze_by_turn(user_report_regular,verify_report_regular)

if __name__ == "__main__":
    main()