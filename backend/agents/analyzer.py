import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

class AnalyzerAgent:
    def __init__(self):
        # Configure Gemini for analysis
        genai.configure(api_key=GOOGLE_API_KEY)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            google_api_key=GOOGLE_API_KEY
        )
        self.analysis_prompt = PromptTemplate(
            input_variables=["expected_results", "actual_log"],
            template="""
            Given the expected results: "{expected_results}" and the actual execution log: "{actual_log}",
            determine if the test case passed or failed. Provide a brief verdict and a reason.
            Format the output as a JSON object with 'verdict' (Passed/Failed) and 'reason'.
            """
        )
        self.analysis_chain = LLMChain(llm=self.llm, prompt=self.analysis_prompt)

    def analyze_test_case(self, test_case_report):
        test_case_id = test_case_report['test_case_id']
        expected_results = test_case_report['expected_results']
        actual_log = test_case_report['actual_log']
        
        try:
            analysis_result_str = self.analysis_chain.run(
                expected_results=expected_results,
                actual_log=actual_log
            )
            analysis_result = json.loads(analysis_result_str)
            verdict = analysis_result.get('verdict', 'Failed')
            reason = analysis_result.get('reason', 'Analysis could not determine a clear outcome.')
        except Exception as e:
            print(f"Error during analysis by LLM: {e}")
            verdict = "Failed"
            reason = f"Analysis failed due to an internal error: {e}"

        # Update the report with analysis results
        test_case_report['analysis'] = {
            'verdict': verdict,
            'reason': reason
        }
        test_case_report['status'] = verdict 

        return test_case_report
