import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import json

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

class PlannerAgent:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=GOOGLE_API_KEY)
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash", # Changed to gemini-1.5-pro for better performance
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY,
            convert_system_message_to_human=True, # Added for Gemini 1.5/2.0 compatibility
            response_mime_type="application/json" # Explicitly request JSON output
        )
        
        self.prompt = PromptTemplate(
            input_variables=["game_url"],
            template="""
            Generate 20 test cases for the math puzzle game at {game_url}.
            Each test case should include:
            1. Test objective
            2. Initial game state
            3. Expected actions
            4. Expected results
            Format the output as a JSON array of structured JSON objects, where each object represents a test case.
            """
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def generate_test_cases(self):
        test_cases = self.chain.run(game_url="https://play.ezygamers.com/")
        return self._parse_test_cases(test_cases)

    def _parse_test_cases(self, raw_output):
        try:
            # Assuming the LLM returns a JSON string that is a list of test case objects
            test_cases_raw = json.loads(raw_output)
            test_cases = []
            for i, case_raw in enumerate(test_cases_raw):
                # Convert keys to snake_case for consistency
                case = {}
                for key, value in case_raw.items():
                    new_key = key.lower().replace(" ", "_")
                    case[new_key] = value
                case['id'] = i + 1 # Ensure each test case has an 'id'
                test_cases.append(case)
            return test_cases
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from LLM: {e}")
            print(f"Raw LLM output: {raw_output}")
            return [] # Return an empty list or handle the error as appropriate