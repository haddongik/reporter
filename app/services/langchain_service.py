import re
import asyncio
import os
from typing import Literal, List, Optional, Dict, Any
from langchain_community.llms.ollama import Ollama
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from app.prompts.battle_prompts import BATTLE_PROMPTS
from battle_report import generate_battle_report

class LangChainService:
    
    def __init__( self, model_type: Literal["local", "openai", "gemini", "claude"] = "local", openai_api_key: str = None, google_api_key: str = None, anthropic_api_key: str = None ):

        # gemini 2.5, claude 3.7 sonnet max, gpt 4-turbo
        self.model_type = model_type
        if model_type == "local":
            self.llm = Ollama(
                model="deepseek-r1:14b",
                base_url="http://localhost:11434"
            )
        elif model_type == "openai":
            if not openai_api_key:
                raise ValueError("OpenAI API 키가 필요합니다.")
            self.llm = ChatOpenAI(
                model="gpt-4-turbo-preview",
                temperature=0.7,
                openai_api_key=openai_api_key
            )
        elif model_type == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                temperature=0.7,
                google_api_key=google_api_key
            )
        elif model_type == "claude":
            self.llm = ChatAnthropic(
                model="claude-3-7-sonnet-max",
                temperature=0.7,
                anthropic_api_key=anthropic_api_key
            )
        else:
            raise ValueError(f"지원하지 않는 모델 타입입니다: {model_type}")

    async def run(self, user_data: Dict[str, Any], verify_data: Dict[str, Any], report_types: List[str]) -> Dict[str, Any]:

        results = {}
        
        # 각 리포트 타입에 대해 리포트 생성
        for report_type in report_types:
            user_report = self.create_battle_report(user_data, report_type, f"user_{report_type}_report.txt")
            verify_report = self.create_battle_report(verify_data, report_type, f"verify_{report_type}_report.txt")
            
            if report_type in ["status", "hp", "attack"]:
                analysis_result = await self.process_analyze_by_turn(user_report, verify_report, report_type.upper())
                results[report_type] = analysis_result
            elif report_type == "full":
                analysis_result = await self.process_analyze_full(user_report, verify_report)
                results[report_type] = analysis_result
        
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

        # 프롬프트 템플릿 생성
        turn_compare_prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS[prompt_type]["turn_compare"]),
            ("user", "{user_turn_content}\n\n{server_turn_content}")
        ])

        summary_prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS[prompt_type]["summary"]),
            ("user", "Here are the turn-by-turn summaries:\n\n{turn_summaries}\n\nPlease provide a comprehensive summary of the battle analysis.")
        ])

        translate_prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS[prompt_type]["translate"]),
            ("user", "Please translate this battle analysis summary into Korean:\n\n{english_summary}")
        ])

        turn_compare_chain = LLMChain(llm=self.llm, prompt=turn_compare_prompt)

        user_turns = self.split_turns(user_report)
        verify_turns = self.split_turns(verify_report)

        turn_summaries = []
        for idx, ((_, user_turn_content), (_, verify_turn_content)) in enumerate(zip(user_turns, verify_turns)):
            turn_result = await turn_compare_chain.arun(
                turn_index=idx,
                user_turn_content=user_turn_content,
                server_turn_content=verify_turn_content
            )
            turn_summaries.append(f"[턴 {idx}] 요약:\n{turn_result}\n")

        # 전체 요약 체인
        final_summary_chain = LLMChain(
            llm=self.llm,
            prompt=summary_prompt,
            output_key="english_summary"
        )

        # 한글 번역 체인
        translate_chain = LLMChain(
            llm=self.llm,
            prompt=translate_prompt,
            output_key="korean_summary"
        )

        # 시퀀셜 체인 생성
        full_chain = SequentialChain(
            chains=[final_summary_chain, translate_chain],
            input_variables=["turn_summaries"],
            output_variables=["english_summary", "korean_summary"],
            verbose=True
        )

        # 체인 실행
        result = await full_chain.ainvoke({"turn_summaries": "\n".join(turn_summaries)})

        return f"=== Summary ===\n{result['korean_summary']}"

    async def process_analyze_full(self, user_report: str, verify_report: str) -> str:

        # 프롬프트 템플릿 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", BATTLE_PROMPTS["FULL"]["turn_compare"]),
            ("user", "{user_report}\n\n{verify_report}")
        ])

        # 체인 생성
        chain = LLMChain(llm=self.llm, prompt=prompt)

        # 체인 실행
        result = await chain.arun(
            user_report=user_report,
            verify_report=verify_report
        )

        return result

    async def process_chat(self, query: str) -> str:

        # 프롬프트 템플릿 생성
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant that provides accurate and concise answers."),
            ("user", "{query}")
        ])

        # 체인 생성
        chain = LLMChain(llm=self.llm, prompt=prompt)

        # 체인 실행
        result = await chain.arun(query=query)

        return result    
    def split_turns(self, log_text: str):
        """## Turn N 기준으로 로그를 턴별로 나눔"""
        parts = re.split(r"(## Turn \d+)", log_text)
        turns = []
        for i in range(1, len(parts), 2):
            turn_id = parts[i].strip()
            content = parts[i+1].strip()
            turns.append((turn_id, content))
        return turns
