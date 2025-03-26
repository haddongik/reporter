import os
import asyncio
from app.services.langchain_service import LangChainService
from app.utils.app_utils import load_json, make_analysis_data

# 현재 실행 폴더 경로 가져오기
current_folder = os.getcwd()
json_file_path = os.path.join(current_folder, "test_lf.json")

async def test_report():
    # JSON 데이터 로드
    json_data = load_json(json_file_path)
    if not json_data:
        print("JSON 데이터를 로드할 수 없습니다.")
        return
    
    # 데이터 추출
    user_data = make_analysis_data(json_data, "result_info", "user_record_minimal")
    verify_data = make_analysis_data(json_data, "result_info", "verify_record_minimal")

    # LangChainService 인스턴스 생성
    langchain_test_service = LangChainService(
        model_type="openai",
        openai_api_key=""
    )

    # 리포트 생성 및 분석 실행
    results = await langchain_test_service.run(
        user_data=user_data,
        verify_data=verify_data,
        report_types=["full", "status", "hp", "attack", "effect"]
    )

    # 결과 출력
    for report_type, result in results.items():
        print(f"\n=== {report_type.upper()} Analysis ===")
        print(result)

async def test_chat():
    # OpenAI API를 사용하는 서비스 인스턴스 생성
    test_service = LangChainService(
        model_type="openai",
        openai_api_key=""
    )
    
    # 간단한 질문 테스트
    test_queries = [
        "안녕하세요! 간단한 테스트입니다.",
        "파이썬으로 'Hello World'를 출력하는 코드를 작성해주세요.",
        "1부터 10까지의 합을 구하는 파이썬 코드를 작성해주세요."
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        try:
            response = await test_service.process_chat(query)
            print(f"답변: {response}")
        except Exception as e:
            print(f"에러 발생: {e}")
        
        # API 호출 간격 조절
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(test_report())
    #asyncio.run(test_chat())