import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

class PlannerAgent:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.8, 
            google_api_key=GOOGLE_API_KEY,
        )
        
        # --- START OF REFINED PROMPT ---
        # This prompt focuses on creating general, high-value test objectives
        # that are likely to be possible on a random game board.
        self.prompt = PromptTemplate(
            template="""
            You are a creative QA tester for a web game called SumLink.
            The fundamental rules are:
            1. Clear pairs of IDENTICAL numbers (e.g., 8 and 8).
            2. Clear pairs of numbers that SUM TO 10 (e.g., 2 and 8).

            Generate 20 high-level test objectives. Focus on what should be tested, not the specific layout.
            Include a mix of positive and negative test objectives.

            Good Examples of Objectives:
            - "Verify the removal of any valid identical pair."
            - "Verify the removal of any valid pair that sums to 10."
            - "Verify that an invalid pair (e.g., summing to 9) cannot be removed."
            - "Verify that clicking the same number twice does not form a pair."

            Bad Examples (Too Specific):
            - "Verify removal of an adjacent 7 and 3." (Relies on a specific board layout)
            - "Verify removal of a 5 at the start of a row and a 5 at the end." (Too specific)

            The JSON object for each test case must have these keys:
            - "test_objective": A short, high-level description of the test's goal.
            - "expected_results": A description of the expected outcome.

            Return ONLY a single, valid JSON array of 20 test case objects.
            \n{format_instructions}\n
            """,
            input_variables=[],
            partial_variables={"format_instructions": JsonOutputParser().get_format_instructions()}
        )
        # --- END OF REFINED PROMPT ---
        
        self.chain = self.prompt | self.llm | JsonOutputParser()

    def generate_test_cases(self):
        print("PlannerAgent: Generating realistic test objectives...")
        test_cases_raw = self.chain.invoke({})
        
        test_cases = []
        for i, case_raw in enumerate(test_cases_raw):
            case = {key.lower().replace(" ", "_"): value for key, value in case_raw.items()}
            case['id'] = i + 1
            test_cases.append(case)
        
        print(f"PlannerAgent: Generated {len(test_cases)} objectives.")
        return test_cases