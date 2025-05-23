import asyncio
import os
from typing import Literal, List, Optional, Dict, Any
from langchain_community.llms.ollama import Ollama
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.prompts.battle_prompts import BATTLE_PROMPTS
from battle_report import generate_battle_report
from app.utils.app_utils import split_turns
from app.config.app_config import app_config  # 설정 파일 import

class SummaryTopic(BaseModel):
    topic: str = Field(description="The topic of the summary")
    summary: str = Field(description="The summary of the topic")
    key_differences: str = Field(description="The key differences between the user and server")
    opinion: str = Field(description="The opinion of the summary and the key differences")

class LangChainService:
    
    def __init__(self, provider: Literal["local", "openai", "google", "anthropic"], model: str, temperature: float):

        self.provider = provider
        self.model = model
        self.temperature = temperature
        
        # LLM 초기화
        if provider == "local":
            self.llm = Ollama(
                model=self.model,
                base_url="http://localhost:11434"
            )
        elif provider == "openai":
            self.llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                openai_api_key=app_config["openai"]["api_key"]
            )
        elif provider == "google":
            self.llm = ChatGoogleGenerativeAI(
                model=self.model,
                temperature=self.temperature,
                google_api_key=app_config["google"]["api_key"]
            )
        elif provider == "anthropic":
            self.llm = ChatAnthropic(
                model=self.model,
                temperature=self.temperature,
                anthropic_api_key=app_config["anthropic"]["api_key"]
            )
        else:
            raise ValueError(f"지원하지 않는 모델 제공자입니다: {provider}")

    async def run(self, user_data: Dict[str, Any], verify_data: Dict[str, Any], report_types: List[str]) -> Dict[str, Any]:
        # 각 리포트 타입에 대한 리포트 생성 및 분석 태스크 생성
        analysis_tasks = []
        for report_type in report_types:
            user_report = self.create_battle_report(user_data, report_type, f"user_{report_type}_report.txt")
            verify_report = self.create_battle_report(verify_data, report_type, f"verify_{report_type}_report.txt")
            
            if report_type in ["status", "hp", "attack"]:
                task = self.process_analyze_by_turn(user_report, verify_report, report_type.upper())
            elif report_type == "full":
                task = self.process_analyze_full(user_report, verify_report)
            
            analysis_tasks.append((report_type, task))
        
        # 모든 분석 태스크를 병렬로 실행
        results = {}
        tasks = [task for _, task in analysis_tasks]
        report_types = [report_type for report_type, _ in analysis_tasks]
        
        # 모든 태스크를 동시에 실행하고 결과를 기다림
        analysis_results = await asyncio.gather(*tasks)
        
        # 결과를 리포트 타입과 매핑
        for report_type, result in zip(report_types, analysis_results):
            results[report_type] = result
        
        return results

    def create_battle_report(self, data: Dict[str, Any], report_type: Optional[str] = None, output_filename: Optional[str] = None) -> Optional[str]:

        # 전투 리포트 생성
        battle_report = generate_battle_report(data, report_type)
        if not battle_report:
            print("리포트 생성에 실패했습니다.")
            return None

        # 파일 저장
        if output_filename:
            try:
                # reports 폴더 없으면 생성
                current_folder = os.getcwd()
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

    async def process_analyze_by_turn(self, user_report: str, verify_report: str, prompt_type: str) -> str:
        """## 턴별 분석을 수행하고 결과를 반환합니다."""
        # 턴별로 분리
        user_turns = split_turns(user_report)
        verify_turns = split_turns(verify_report)
        
        # 턴 비교 프롬프트 템플릿 생성
        turn_compare_prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS[prompt_type]["turn_compare"]),
            ("user", """Turn {turn_index} Analysis:
            Previous Turn Summary: {previous_summary}
            User Turn Content: {user_turn_content}
            Server Turn Content: {server_turn_content}
            Please analyze this turn considering the previous turn's summary.""")
        ])
        
        # 요약 프롬프트 템플릿 생성
        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS[prompt_type]["summary"]),
            ("user", """Based on the turn-by-turn analysis, provide a comprehensive summary:
            {turn_summaries}
            Please provide a detailed summary of the battle analysis.""")
        ])

        translate_prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS["TRANSLATE"]),
            ("user", "Please translate this battle analysis summary into Korean:\n\n{summary}")
        ])

        # 체인 생성
        turn_compare_chain = LLMChain(
            llm=self.llm,
            prompt=turn_compare_prompt,
            output_key="turn_analysis"
        )
        
        summary_chain = LLMChain(
            llm=self.llm,
            prompt=summary_prompt,
            output_key="summary"
        )

        translate_chain = LLMChain(
            llm=self.llm,
            prompt=translate_prompt,
            output_key="korean_summary"
        )

        # 순차적 체인 생성
        turn_analysis_chain = SequentialChain(
            chains=[turn_compare_chain, summary_chain],
            input_variables=["turn_index", "user_turn_content", "server_turn_content", "previous_summary", "turn_summaries"],
            output_variables=["turn_analysis", "summary"],
            verbose=True
        )
        
        turn_summaries = []
        previous_summary = "No previous turn data available."
        
        for idx, ((_, user_turn_content), (_, verify_turn_content)) in enumerate(zip(user_turns, verify_turns)):
            try:
                # 현재 턴 분석
                result = await turn_analysis_chain.ainvoke({
                    "turn_index": idx,
                    "user_turn_content": user_turn_content,
                    "server_turn_content": verify_turn_content,
                    "previous_summary": previous_summary,
                    "turn_summaries": "\n".join(turn_summaries) if turn_summaries else "No previous turns analyzed."
                })
                
                # 현재 턴의 분석 결과 저장
                turn_summaries.append(f"[Turn {idx}] Summary:\n{result['turn_analysis']}\n")
                
                # 다음 턴을 위한 이전 턴 요약 업데이트
                previous_summary = result['turn_analysis']
                
            except Exception as e:
                print(f"Turn {idx} analysis error: {e}")
                await asyncio.sleep(5)
                try:
                    result = await turn_analysis_chain.ainvoke({
                        "turn_index": idx,
                        "user_turn_content": user_turn_content,
                        "server_turn_content": verify_turn_content,
                        "previous_summary": previous_summary,
                        "turn_summaries": "\n".join(turn_summaries) if turn_summaries else "No previous turns analyzed."
                    })
                    turn_summaries.append(f"[Turn {idx}] Summary:\n{result['turn_analysis']}\n")
                    previous_summary = result['turn_analysis']
                except Exception as e:
                    print(f"Turn {idx} retry failed: {e}")
                    turn_summaries.append(f"[Turn {idx}] Analysis failed\n")
            
            # 각 턴 분석 사이에 2초 대기
            await asyncio.sleep(30)
        
        # 최종 요약 생성
        # final_analysis_chain = SequentialChain(
        #    chains=[summary_chain, translate_chain],
        #    input_variables=["turn_summaries"],
        #    output_variables=["korean_summary"],
        #    verbose=True
        # )

        # final_summary = await final_analysis_chain.ainvoke({
        #    "turn_summaries": "\n".join(turn_summaries)
        # })

        print("turn_summaries 내용:", turn_summaries)  # 디버깅을 위해 추가

        json_parser = JsonOutputParser(pydantic_object=SummaryTopic)
        json_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert in battle log and security analysis.
            You must respond in the following JSON format:
            {{
                "topic": "주제",
                "summary": "요약",
                "key_differences": "주요 차이점",
                "opinion": "의견"
            }}
            IMPORTANT: Your response must be valid JSON with all fields present."""),
            ("user", """Based on the turn-by-turn analysis, provide a comprehensive summary:
            {turn_summaries}
            Please provide a detailed summary of the battle analysis.""")
        ])

        # 파서의 형식 지시사항 확인
        format_instructions = json_parser.get_format_instructions()
        print("파서 형식 지시사항:", format_instructions)  # 디버깅을 위해 추가

        json_prompt = json_prompt.partial(format_instructions=format_instructions)
        json_chain = json_prompt | self.llm

        try:
            raw_response = await json_chain.ainvoke({"turn_summaries": "\n".join(turn_summaries)})
            print("LLM 원본 응답:", raw_response)  # 디버깅을 위해 추가
        except Exception as e:
            print(f"에러 발생: {str(e)}")
            return None

        try:
            # AIMessage 객체에서 content만 추출
            json_content = raw_response.content       
            # JSON 문자열에서 ```json과 ``` 제거
            json_content = json_content.replace('```json', '').replace('```', '').strip()
            # JSON 파싱
            json_result = json_parser.parse(json_content)
            print(json_result)
        except ValueError as e:
            print(f"JSON 파싱 에러: {str(e)}")
            return None
        except Exception as e:
            print(f"예상치 못한 에러: {str(e)}")
            return None
        
        return json_result

    async def process_analyze_full(self, user_report: str, verify_report: str) -> str:

        prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS["FULL"]["turn_compare"]),
            ("user", "{user_report}\n\n{verify_report}")
        ])

        chain = LLMChain(llm=self.llm, prompt=prompt)

        result = await chain.arun(
            user_report=user_report,
            verify_report=verify_report
        )

        return result

    async def process_chat(self, query: str) -> str:

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that provides accurate and concise answers."),
            ("user", "{query}")
        ])

        chain = LLMChain(llm=self.llm, prompt=prompt)

        result = await chain.arun(query=query)

        return result    