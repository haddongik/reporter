from langchain_community.llms.ollama import Ollama
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

class LangChainService:
    def __init__(self):
        self.llm = Ollama(
            model="deepseek-r1:14b",
            base_url="http://localhost:11434"
        )
        
    async def process_query(self, query: str):
        prompt = PromptTemplate(
            input_variables=["query"],
            template="질문: {query}\n답변:"
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = await chain.arun(query=query)
        return response 