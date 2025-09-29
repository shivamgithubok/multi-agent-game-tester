import json
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

class AnalyzerAgent:
    def __init__(self):
        genai.configure(api_key=GOOGLE_API_KEY)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0, google_api_key=GOOGLE_API_KEY)

        self.analysis_prompt = PromptTemplate(
            template="""
            You are a meticulous Software Quality Assurance engineer.
            Your task is to analyze test results by comparing what was expected with what actually happened.
            A test PASSES only if the actual outcome matches the expected outcome. Otherwise, it FAILS.

            - Expected Results: "{expected_results}"
            - Actual Observed Results: "{actual_results}"

            Analyze these results and provide your verdict.
            Return a single JSON object with two keys: "verdict" (string: "Passed" or "Failed") and "reason" (string: a brief explanation).
            \n{format_instructions}\n
            """,
            input_variables=["expected_results", "actual_results"],
            partial_variables={"format_instructions": JsonOutputParser().get_format_instructions()}
        )
        self.chain = self.analysis_prompt | self.llm | JsonOutputParser()

    def analyze_test_case(self, test_case_report):
        test_case_id = test_case_report['test_case_id']
        resolution_name = test_case_report.get('resolution_name', 'Desktop') # Get the name, with a default
        print(f"AnalyzerAgent: Analyzing Test Case {test_case_id} for {resolution_name}...")
        
        try:
            # ... (analysis logic is correct) ...
            analysis_result = self.chain.invoke({
                "expected_results": test_case_report['expected_results'],
                "actual_results": test_case_report['actual_results']
            })
            verdict = analysis_result.get('verdict', 'Failed')
            reason = analysis_result.get('reason', 'LLM analysis did not provide a reason.')
            
        except Exception as e:
            print(f"Error during analysis by LLM: {e}")
            verdict = "Failed"
            reason = f"Analysis failed due to a processing error: {e}"

        test_case_report['analysis'] = {'verdict': verdict, 'reason': reason}
        test_case_report['status'] = verdict
        
        # --- START OF FIX ---
        # Construct the final report filename using the provided resolution name
        resolution_tuple = test_case_report.get('resolution', (1920, 1080))
        report_file_path = os.path.join("report", f"test_case_{test_case_id}_{resolution_name}_{resolution_tuple[0]}x{resolution_tuple[1]}_report.json")
        # --- END OF FIX ---
        
        with open(report_file_path, "w") as report_file:
            json.dump(test_case_report, report_file, indent=4)
        
        print(f"AnalyzerAgent: Verdict for Test Case {test_case_id} on {resolution_name} is '{verdict}'.")
        return test_case_report