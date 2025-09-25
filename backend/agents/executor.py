import json
import os
from selenium import webdriver
import time
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY environment variable is not set")

class ExecutorAgent:
    def __init__(self, report_dir="report"):
        self.report_dir = report_dir
        # Ensure the report directory exists
        if not os.path.exists(self.report_dir):
            os.makedirs(self.report_dir)
        
        # Configure Gemini for action interpretation
        genai.configure(api_key=GOOGLE_API_KEY)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            api_key=GOOGLE_API_KEY
        )
        self.action_prompt = PromptTemplate(
            input_variables=["game_url", "expected_actions"],
            template="""
            Given the game at {game_url} and the expected actions: {expected_actions},
            generate a Python list of Selenium WebDriver commands to perform these actions.
            Each command should be a dictionary with 'method' (e.g., 'click', 'send_keys', 'get')
            and 'args' (a dictionary of arguments).
            For example: 
            [{{"method": "get", "args": {{"url": "https://play.ezygamers.com/"}}}},
             {{"method": "find_element_by_id", "args": {{"id": "some_button"}}}},
             {{"method": "click", "args": {{}}}},
             {{"method": "find_element_by_name", "args": {{"name": "some_input"}}}},
             {{"method": "send_keys", "args": {{"keys": "123"}}}}]
            Only provide the list of commands, no extra text.
            """
        )
        self.action_chain = LLMChain(llm=self.llm, prompt=self.action_prompt)

    def execute_test_case(self, test_case):
        test_case_id = test_case['id']
        game_url = "https://play.ezygamers.com/"
        expected_actions_description = test_case['expected_actions']

        # Setup Selenium WebDriver
        driver = webdriver.Chrome()

        # Open the game URL
        driver.get(game_url)
        time.sleep(4) # Give some time for the page to load

        # Interpret and execute actions using LLM
        try:
            selenium_commands_str = self.action_chain.run(
                game_url=game_url,
                expected_actions=expected_actions_description
            )
            
            # Debugging: Print raw LLM output for Selenium commands
            print(f"Raw LLM output for Selenium commands (Test Case {test_case_id}): {selenium_commands_str}")

            selenium_commands = json.loads(selenium_commands_str)
            
            for command in selenium_commands:
                method = command['method']
                args = command.get('args', {})
                
                # Special handling for element-based actions
                if method.startswith("find_element_"):
                    element = getattr(driver, method)(**args)
                    # Assuming the next command is an action on this element
                    # This is a simplification; a more robust solution would chain calls
                    continue
                elif method in ['click', 'send_keys'] and 'element' in locals():
                    getattr(element, method)(**args)
                else:
                    getattr(driver, method)(**args)
                time.sleep(5) # Small delay between actions

        except Exception as e:
            print(f"Error executing Selenium actions: {e}")
            status = "Failed"
            log_content = f"Test case {test_case_id} failed: {e}"
        else:
            status = "Success"
            log_content = f"Test case {test_case_id} executed successfully."

        # Capture screenshot
        screenshot_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_screenshot.png")
        driver.save_screenshot(screenshot_path)

        # Generate a JSON report
        report_data = {
            "test_case_id": test_case_id,
            "status": status,
            "objective": test_case.get('test_objective', 'N/A'),
            "initial_state": test_case.get('initial_game_state', 'N/A'),
            "expected_actions": test_case.get('expected_actions', 'N/A'),
            "expected_results": test_case.get('expected_results', 'N/A'),
            "actual_log": log_content,
            "artifacts": {
                "screenshot": f"test_case_{test_case_id}_screenshot.png",
                # Removed log from artifacts as content is directly in actual_log
                # "log": f"test_case_{test_case_id}_log.txt",
            }
        }

        # Save the report data to a JSON file
        report_file_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_report.json")
        try:
            with open(report_file_path, "w") as report_file:
                json.dump(report_data, report_file, indent=4)
        except Exception as e:
            print(f"Error writing JSON report: {e}")
            raise

        driver.quit()

        return report_data