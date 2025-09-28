import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

class RankerAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0, google_api_key=GOOGLE_API_KEY)
        
        self.prompt = PromptTemplate(
            template="""
            You are a seasoned QA Lead responsible for prioritizing testing efforts.
            You are given a list of test cases, each with an 'id' and 'test_objective'.
            Your task is to select the 10 most valuable test cases to run.

            Prioritize tests that cover:
            1. Core Functionality: Basic successful matches (both identical and sum-to-10).
            2. Negative Scenarios: Attempts to make invalid matches.
            3. Edge Cases: Scenarios that might break the game (e.g., interacting with an empty board).
            4. Uniqueness: Ensure a diverse range of scenarios is covered.

            Analyze the following test cases:
            {test_cases_str}

            Return a single JSON object with one key, "top_10_ids", which is a list of the 10 integer IDs you have selected.
            \n{format_instructions}\n
            """,
            input_variables=["test_cases_str"],
            partial_variables={"format_instructions": JsonOutputParser().get_format_instructions()}
        )

        self.chain = self.prompt | self.llm | JsonOutputParser()

    def rank_test_cases(self, test_cases):
        if not test_cases:
            return []
            
        print("RankerAgent: Using LLM to intelligently rank test cases...")
        # Format the test cases for the prompt
        test_cases_str = "\n".join([f"- ID {tc['id']}: {tc['test_objective']}" for tc in test_cases])
        
        response = self.chain.invoke({"test_cases_str": test_cases_str})
        top_ids = response.get("top_10_ids", [])
        
        print(f"RankerAgent: Selected top 10 test case IDs: {top_ids}")
        
        # Filter the original list to return the full test case objects for the top IDs
        ranked_test_cases = [tc for tc in test_cases if tc['id'] in top_ids]
        
        # Fallback to simple sorting if LLM fails
        if not ranked_test_cases:
            print("RankerAgent: LLM ranking failed, falling back to simple sort.")
            return sorted(test_cases, key=lambda x: x['id'])[:10]

        return ranked_test_cases