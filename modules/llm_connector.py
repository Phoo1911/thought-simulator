from openai import OpenAI as OpenAIClient 
from langchain_community.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os

class LLMConnector:
    def __init__(self, api_key=None, model_name="deepseek-chat"):
        print(f"[🔑 INIT] API Key received: {api_key is not None}")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.client = OpenAIClient(api_key=self.api_key)  # ✅ 클라이언트 객체 생성
        self.model_name = model_name

    def generate(self, prompt, max_tokens=2000):
        print("[💬] Sending prompt to OpenAI API...")
        """Generate response using OpenAI API directly"""
        try:
            response = self.client.chat.completions.create(  # ✅ 새 방식
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a thought simulator that shows detailed thinking processes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def generate_with_langchain(self, prompt_template, input_variables):
        """Generate response using LangChain (alternative approach)"""
        llm = OpenAI(model_name=self.model_name, temperature=0.7)
        prompt = PromptTemplate(
            input_variables=list(input_variables.keys()),
            template=prompt_template
        )
        chain = LLMChain(llm=llm, prompt=prompt)
        return chain.run(**input_variables)