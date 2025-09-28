from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

class SolverAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.0, google_api_key=GOOGLE_API_KEY)

        # --- REFINED PROMPT FOR MORE ACCURATE PLANS ---
        self.prompt = PromptTemplate(
            template="""
            You are an expert player of the SumLink game. Your task is to find a valid move on a given game board that satisfies a specific test objective.

            Game Rules:
            - A valid move is clicking a pair of numbers that are either IDENTICAL or sum to 10.
            - The pair must have a clear path between them (only empty spaces or no other numbers).
            - The board is a list of all currently active (clickable) numbers.

            Your Task:
            Analyze the current board state and the test objective. Find the first valid pair that satisfies the objective.
            Provide the numbers and their 1-based index (position) IN THE PROVIDED LIST.

            Current Board State (list of active numbers):
            {board_state}

            Test Objective:
            {test_objective}

            If a valid move exists, return a JSON object with keys "first_number", "first_index", "second_number", "second_index".
            If NO valid move exists that satisfies the objective, return a JSON object with "actionable" set to false.

            Example:
            Board: ["8", "1", "9", "8", "3"]
            Objective: "Verify removal of an identical pair."
            Output: {{"first_number": "8", "first_index": 1, "second_number": "8", "second_index": 2}}

            Now, analyze the given board and objective.
            \n{format_instructions}\n
            """,
            input_variables=["board_state", "test_objective"],
            partial_variables={"format_instructions": JsonOutputParser().get_format_instructions()}
        )
        self.chain = self.prompt | self.llm | JsonOutputParser()

    def create_action_plan(self, board_state, test_objective):
        print(f"SolverAgent: Finding a move for objective '{test_objective}' on board {board_state}")
        if not board_state:
            return {"actionable": False, "reason": "The board is empty."}
        
        plan = self.chain.invoke({
            "board_state": str(board_state),
            "test_objective": test_objective
        })
        print(f"SolverAgent: Generated plan: {plan}")
        return plan