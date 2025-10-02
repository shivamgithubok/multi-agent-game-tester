from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


# ... imports ...
class SolverAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro-latest", temperature=0.0, google_api_key=GOOGLE_API_KEY)
        self.prompt = PromptTemplate(
            template="""
            You are an expert game player. Your task is to find a valid pair to click based on a list of available numbers and a test objective.
            The input is a list of dictionaries, where each dictionary has a 'text' (the number) and an 'index' (its position on the board).
            Game Rules: A valid pair is two numbers that are either IDENTICAL or sum to 10.

            Your Task:
            Analyze the list of available numbers and the objective. Find the best pair that satisfies the objective.
            Return a JSON object with the key "indices_to_click", which is a list containing the two integer indices of the elements you chose from the original list.
            If no valid move exists that satisfies the objective, return a JSON object with the key "actionable" set to false.

            Available Numbers (List of Dictionaries):
            {elements_info}

            Test Objective:
            {test_objective}

            Example:
            Available Numbers: [{{"text": "8", "index": 0}}, {{"text": "1", "index": 1}}, {{"text": "9", "index": 2}}, {{"text": "8", "index": 3}}]
            Objective: "Verify removal of an identical pair."
            Output: {{"indices_to_click": [0, 3]}}
            \n{format_instructions}\n
            """,
            input_variables=["elements_info", "test_objective"],
            partial_variables={"format_instructions": JsonOutputParser().get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | JsonOutputParser()

    def create_action_plan(self, active_elements, test_objective):
        if not active_elements:
            return {"actionable": False, "reason": "The board is empty."}
        
        # Create a simplified list for the LLM
        elements_info = [{"text": el.text, "index": i} for i, el in enumerate(active_elements)]
        print(f"SolverAgent: Finding a move for '{test_objective}' from available elements: {elements_info}")
        
        plan = self.chain.invoke({
            "elements_info": str(elements_info),
            "test_objective": test_objective
        })
        print(f"SolverAgent: Generated plan: {plan}")
        return plan