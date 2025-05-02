import os
import asyncio
from app.services.langchain_service import LangChainService
from app.utils.app_utils import load_json, make_analysis_data
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_teddynote.graphs import visualize_graph
from app.config.app_config import app_config

class State(TypedDict):
    # 메시지 정의(list type 이며 add_messages 함수를 사용하여 메시지를 추가)
    messages: Annotated[list, add_messages]

async def test_report():

    # 현재 실행 폴더 경로 가져오기
    current_folder = os.getcwd()
    json_file_path = os.path.join(current_folder, "test_lf.json")

    # JSON 데이터 로드
    json_data = load_json(json_file_path)
    if not json_data:
        print("JSON 데이터를 로드할 수 없습니다.")
        return
    
    # 데이터 추출
    user_data = make_analysis_data(json_data, "result_info", "user_record_minimal")
    verify_data = make_analysis_data(json_data, "result_info", "verify_record_minimal")

    # LangChainService 인스턴스 생성
    langchain_test_service = LangChainService( provider="openai", model="gpt-4o", temperature=0.7 )

    # 리포트 생성 및 분석 실행
    results = await langchain_test_service.run(
        user_data=user_data,
        verify_data=verify_data,
        report_types=["status", "hp"]
        #report_types=["full", "status", "hp", "attack", "effect"]
    )

    # 결과 출력
    for report_type, result in results.items():
        print(f"\n=== {report_type.upper()} Analysis ===")
        print(result)

async def test_chat():

    # LangChainService 인스턴스 생성
    langchain_test_service = LangChainService( provider="openai", model="gpt-4o", temperature=0.7 )
    
    test_queries = [
        "안녕하세요! 간단한 테스트입니다.",
        "파이썬으로 'Hello World'를 출력하는 코드를 작성해주세요.",
        "1부터 10까지의 합을 구하는 파이썬 코드를 작성해주세요."
    ]
    
    for query in test_queries:
        print(f"\n질문: {query}")
        try:
            response = await langchain_test_service.process_chat(query)
            print(f"답변: {response}")
        except Exception as e:
            print(f"에러 발생: {e}")
        
        # API 호출 간격 조절
        await asyncio.sleep(1)

def test_langgraph():

        
    def chatbot(state: State):
        # 메시지 호출 및 반환
        return {"messages": [llm.invoke(state["messages"])]}

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        openai_api_key=app_config["openai"]["api_key"]
    )

    # 그래프 생성
    graph_builder = StateGraph(State)

    # 노드 이름, 함수 혹은 callable 객체를 인자로 받아 노드를 추가
    graph_builder.add_node("chatbot", chatbot)

    ###### STEP 4. 그래프 엣지(Edge) 추가 ######
    # 시작 노드에서 챗봇 노드로의 엣지 추가
    graph_builder.add_edge(START, "chatbot")

    # 그래프에 엣지 추가
    graph_builder.add_edge("chatbot", END)

    ###### STEP 5. 그래프 컴파일(compile) ######
    # 그래프 컴파일
    graph = graph_builder.compile()

    ###### STEP 6. 그래프 시각화 ######
    # 그래프 시각화
    visualize_graph(graph)

    ###### STEP 7. 그래프 실행 ######
    question = "서울의 유명한 맛집 TOP 10 추천해줘"

    # 그래프 이벤트 스트리밍
    for event in graph.stream({"messages": [("user", question)]}):
        # 이벤트 값 출력
        for value in event.values():
            print(value["messages"][-1].content)

if __name__ == "__main__":
    #asyncio.run(test_report())
    #asyncio.run(test_chat())
    test_langgraph()