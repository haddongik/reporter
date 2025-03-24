import re
from langchain_community.llms.ollama import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class LangChainService:
    def __init__(self):
        self.llm = Ollama(
            model="deepseek-r1:14b",
            base_url="http://localhost:11434"
        )
        
    async def process_analyze(self, original_text: str, comparison_text: str):
        analyze_prompt = PromptTemplate(
            input_variables=["original", "comparison"],
            template="""
            유저 데이터와 서버 데이터를 분석하여 차이점과 유사점을 찾아주세요.
            서버 데이터는 완전하게 오차없는 데이터이고,
            유저 데이터는 오차(해킹포함)가 발생할 수 있는 데이터입니다.

            유저 데이터:
            {original}

            서버 데이터:
            {comparison}

            분석 포인트:
            1. 주요 차이점
            2. 유사한 부분
            3. 오차가 발생했을 경우, 유저 데이터가 큰 이득을 얻었는지 혹은 큰 손해를 입었는지
            4. 전체적인 평가(오탐으로 볼것인지 해킹으로 볼것인지)
            5. 유저 데이터가 해킹으로 볼 경우, 해킹 방법을 찾아주세요.
            6. 유저 데이터가 오탐으로 볼 경우, 오탐 방법을 찾아주세요.
            상세 분석 결과:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=analyze_prompt)
        response = await chain.arun(
            original=original_text,
            comparison=comparison_text
        )

        return response
    
    async def process_analyze_by_turn(self, original_text: str, comparison_text: str):

        turn_compare_prompt = PromptTemplate(
            input_variables=["turn_index", "user_turn_content", "server_turn_content"],
            template="""
            턴 {turn_index}의 유저 데이터와 서버 데이터를 비교하여 분석해주세요.

            [유저 턴 로그]
            {user_turn_content}

            [서버 턴 로그]
            {server_turn_content}

            분석 포인트:
            - 행동/데미지/효과 등에서 차이점
            - 유사한 점
            - 유저가 이득을 본 부분
            - 의심되는 조작 여부
            간단 요약 (한글로):
            """
        )

        final_summary_prompt = PromptTemplate(
            input_variables=["turn_summaries"],
            template="""
            아래는 턴별 로그 비교 분석 결과입니다:

            {turn_summaries}

            이 내용을 바탕으로 전체적인 판단을 내려주세요.

            분석 포인트:
            1. 전체적인 차이 경향
            2. 유저 데이터에 해킹 또는 오탐 의심 정황
            3. 유저가 얻은 이득/손해
            4. 해킹으로 판단되는 경우, 어떤 방식으로 조작되었는지
            5. 오탐일 경우, 어떤 패턴 때문에 오탐으로 보였는지

            전체 판단 요약:
            """
        )

        turn_compare_chain = LLMChain(llm=self.llm, prompt=self.turn_compare_prompt)
        final_summary_chain = LLMChain(llm=self.llm, prompt=self.final_summary_prompt)

        user_turns = self.split_turns(original_text)
        server_turns = self.split_turns(comparison_text)

        turn_summaries = []
        for idx, ((_, user_turn_content), (_, server_turn_content)) in enumerate(zip(user_turns, server_turns)):
            turn_result = await self.turn_compare_chain.arun(
                turn_index=idx,
                user_turn_content=user_turn_content,
                server_turn_content=server_turn_content
            )
            turn_summaries.append(f"[턴 {idx}] 요약:\n{turn_result}\n")

        # 전체 요약 요청
        final_result = await self.final_summary_chain.arun(
            turn_summaries="\n".join(turn_summaries)
        )

        return {
            "turn_analyses": turn_summaries,
            "final_summary": final_result
        }
    
    async def process_chat(self, query: str):
        prompt = PromptTemplate(
            input_variables=["query"],
            template="질문: {query}\n답변:"
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(query=query)
        return response
    
    def split_turns(self, log_text: str):
        """## 턴 N 기준으로 로그를 턴별로 나눔"""
        parts = re.split(r"(## 턴 \d+)", log_text)
        turns = []
        for i in range(1, len(parts), 2):
            turn_id = parts[i].strip()
            content = parts[i+1].strip()
            turns.append((turn_id, content))
        return turns