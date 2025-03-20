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

            상세 분석 결과:
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=analyze_prompt)
        response = await chain.arun(
            original=original_text,
            comparison=comparison_text
        )

        return response

    async def process_chat(self, query: str):
        prompt = PromptTemplate(
            input_variables=["query"],
            template="질문: {query}\n답변:"
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(query=query)
        return response