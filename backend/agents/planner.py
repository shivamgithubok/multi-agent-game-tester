import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

class PlannerAgent:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.8, google_api_key=GOOGLE_API_KEY)
        
        self.prompt = PromptTemplate(
            template="""
            You are a world-class QA engineer testing a web game called SumLink. Your task is to generate 10 creative, high-value test objectives.

            First, you MUST prioritize the instructions from the human tester. This is your primary goal.
            Human Guidance:
            ---
            {human_guidance}
            ---

            Second, use the context from past test failures to create new tests that probe those specific weaknesses.
            Past Failures Context (retrieved from memory):
            ---
            {context}
            ---

            If there's no specific guidance, generate a diverse set of tests covering the game's core rules (clearing identical pairs and pairs that sum to 10) and negative cases.

            Return ONLY a single, valid JSON array of 10 test case objects. Each object must have keys "test_objective" and "expected_results".
            \n{format_instructions}\n
            """,
            input_variables=["human_guidance", "context"],
            partial_variables={"format_instructions": JsonOutputParser().get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | JsonOutputParser()

    def generate_test_cases(self, context: str, human_guidance: str):
        print("PlannerAgent: Generating objectives using human guidance and past context...")
        try:
            test_cases_raw = self.chain.invoke({"context": context, "human_guidance": human_guidance})
            test_cases = [{'id': 200 + i, **{k.lower().replace(" ", "_"): v for k, v in case.items()}} for i, case in enumerate(test_cases_raw)]
            print(f"PlannerAgent: Generated {len(test_cases)} AI-driven objectives.")
            return test_cases
        except Exception as e:
            print(f"PlannerAgent: Failed to generate test cases due to an error (possibly from the API): {e}. Returning an empty list.")
            return []

# import os
# from dotenv import load_dotenv
# import google.generativeai as genai
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.prompts import PromptTemplate
# from langchain_core.output_parsers import JsonOutputParser

# load_dotenv()

# GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

# class PlannerAgent:
#     def __init__(self):
#         genai.configure(api_key=GOOGLE_API_KEY)
#         self.llm = ChatGoogleGenerativeAI(
#             model="gemini-2.0-flash", 
#             temperature=0.8,
#             google_api_key=GOOGLE_API_KEY,
#         )
        
#         self.prompt = PromptTemplate(
#             template="""
#             You are a highly intelligent QA tester for a web game called SumLink.
#             Your goal is to generate 20 diverse and effective high-level test objectives.

#             To help you improve, here is a summary of test objectives that have failed in the past. 
#             Use these as inspiration to create new, more challenging, or more specific tests to probe these areas of weakness. 
#             If there are no past failures, focus on broad coverage of game rules (identical pairs, sum-to-10 pairs, and invalid pairs).

#             Past Failures Context:
#             ---
#             {context}
#             ---

#             Generate ONLY a single, valid JSON array of 20 test case objects. Each object must have these keys:
#             - "test_objective": A short, high-level description of the test's goal.
#             - "expected_results": A description of the expected outcome.
#             \n{format_instructions}\n
#             """,
#             input_variables=["context"],
#             partial_variables={"format_instructions": JsonOutputParser().get_format_instructions()}
#         )
#         self.chain = self.prompt | self.llm | JsonOutputParser()

#     def generate_test_cases(self, context: str):
#         print("PlannerAgent: Generating realistic test objectives using past context...")
#         test_cases_raw = self.chain.invoke({"context": context})
        
#         test_cases = []
#         for i, case_raw in enumerate(test_cases_raw):
#             case = {key.lower().replace(" ", "_"): value for key, value in case_raw.items()}
#             case['id'] = i + 1
#             test_cases.append(case)
        
#         print(f"PlannerAgent: Generated {len(test_cases)} objectives.")
#         return test_cases