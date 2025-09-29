import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
import time
from dotenv import load_dotenv
from agents.solver import SolverAgent

# ... imports ...
class ExecutorAgent:
    def __init__(self, solver: SolverAgent, report_dir="report"):
        self.report_dir = report_dir
        self.solver = solver

    def execute_test_case(self, test_case: dict, resolution: tuple):
        test_case_id, objective = test_case['id'], test_case['test_objective']
        resolution_str = f"{resolution[0]}x{resolution[1]}"
        print(f"\nExecutorAgent: Starting session for TC {test_case_id} at {resolution_str}: {objective}")
        
        driver = None
        report_data = {
            "test_case_id": test_case_id, "status": "Failed",
            "objective": objective,
            "expected_results": test_case.get('expected_results'),
            "actual_log": "Test execution did not start.", 
            "actual_results": "", "artifacts": {"screenshots": []}
        }
        board_state_before = "Not captured"
        action_plan = {}

        try:
            driver = webdriver.Chrome()
            driver.set_window_size(resolution[0], resolution[1])
            wait = WebDriverWait(driver, 20)

            driver.get("https://play.ezygamers.com/")
            wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='English']"))).click()
            new_game_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='New Game']")))
            driver.execute_script("localStorage.setItem('sumLinkTutorialCompleted', 'true');")
            new_game_button.click()
            wait.until(EC.visibility_of_element_located((By.ID, "main-game-grid")))
            
            board_state_before = self._get_board_state(driver, wait)
            before_screenshot_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_{resolution_str}_before.png")
            driver.save_screenshot(before_screenshot_path)
            report_data["artifacts"]["screenshots"].append(os.path.basename(before_screenshot_path))
            
            action_plan = self.solver.create_action_plan(board_state_before, objective)

            if not action_plan.get("actionable", True):
                report_data['status'] = "Passed"
                report_data['actual_log'] = f"Solver correctly determined no action was possible on {resolution_str}. Board: {board_state_before}"
            else:
                first_num, first_idx = action_plan['first_number'], action_plan['first_index']
                second_num, second_idx = action_plan['second_number'], action_plan['second_index']

                xpath1 = f"(//div[contains(@class, 'grid-cell') and not(contains(@class, 'blurred')) and not(contains(@class, 'cleared')) and normalize-space()='{first_num}'])[{first_idx}]"
                xpath2 = f"(//div[contains(@class, 'grid-cell') and not(contains(@class, 'blurred')) and not(contains(@class, 'cleared')) and normalize-space()='{second_num}'])[{second_idx}]"
                
                wait.until(EC.element_to_be_clickable((By.XPATH, xpath1))).click()
                time.sleep(0.5)
                wait.until(EC.element_to_be_clickable((By.XPATH, xpath2))).click()
                
                time.sleep(2)
                board_state_after = self._get_board_state(driver, wait)
                after_screenshot_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_{resolution_str}_after.png")
                driver.save_screenshot(after_screenshot_path)
                report_data["artifacts"]["screenshots"].append(os.path.basename(after_screenshot_path))
                report_data['status'] = "Pending Analysis"
                report_data['actual_results'] = f"Board before: {board_state_before}. Board after: {board_state_after}."

        except Exception as e:
            plan_str = f"the {action_plan.get('first_index', 'N/A')}-th '{action_plan.get('first_number', 'N/A')}'"
            error_message = f"Failure on {resolution_str}: Timed out trying to click {plan_str}. Board state: {board_state_before}"
            report_data['actual_log'] = error_message
        
        finally:
            if driver:
                final_screenshot_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_{resolution_str}_final.png")
                driver.save_screenshot(final_screenshot_path)
                report_data["artifacts"]["screenshots"].append(os.path.basename(final_screenshot_path))
                driver.quit()
        
        return report_data

    def _get_board_state(self, driver, wait: WebDriverWait):
        # ... this method is correct ...
        pass

# ... rest of the code ...
# import json
# import os
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException, TimeoutException
# import time
# from dotenv import load_dotenv
# from agents.solver import SolverAgent

# class ExecutorAgent:
#     def __init__(self, solver: SolverAgent, report_dir="report"):
#         self.report_dir = report_dir
#         self.solver = solver

#     def _get_board_state(self, driver, wait: WebDriverWait):
#         try:
#             grid = wait.until(EC.presence_of_element_located((By.ID, "main-game-grid")))
#             wait.until(EC.presence_of_element_located((By.XPATH, ".//div[contains(@class, 'grid-cell')]")))
#             active_cells = grid.find_elements(By.XPATH, ".//div[contains(@class, 'grid-cell') and not(contains(@class, 'blurred')) and not(contains(@class, 'cleared'))]")
#             return [cell.text.strip() for cell in active_cells if cell.text.strip().isdigit()]
#         except Exception as e:
#             print(f"Error while reading board state: {e}")
#             return []

#     # --- START OF REVERTED AND CORRECTED CODE ---
#     # This method now handles the entire lifecycle for a single test case.
#     def execute_test_case(self, test_case: dict):
#         test_case_id, objective = test_case['id'], test_case['test_objective']
#         print(f"\nExecutorAgent: Starting new session for Test Case {test_case_id}: {objective}")
        
#         driver = None # Initialize driver to None
#         report_data = {
#             "test_case_id": test_case_id, "status": "Failed",
#             "objective": objective,
#             "expected_results": test_case.get('expected_results'),
#             "actual_log": "Test execution did not start.", 
#             "actual_results": "", "artifacts": {"screenshots": []}
#         }
#         board_state_before = "Not captured"
#         action_plan = {}

#         try:
#             # --- Setup is now INSIDE the try block ---
#             driver = webdriver.Chrome()
#             driver.maximize_window()
#             wait = WebDriverWait(driver, 20)
#             driver.get("https://play.ezygamers.com/")

#             wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='English']"))).click()
#             new_game_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='New Game']")))
#             driver.execute_script("localStorage.setItem('sumLinkTutorialCompleted', 'true');")
#             new_game_button.click()
#             wait.until(EC.visibility_of_element_located((By.ID, "main-game-grid")))

#             # --- Test execution logic remains the same ---
#             board_state_before = self._get_board_state(driver, wait)
#             before_screenshot_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_before.png")
#             driver.save_screenshot(before_screenshot_path)
#             report_data["artifacts"]["screenshots"].append(os.path.basename(before_screenshot_path))
            
#             action_plan = self.solver.create_action_plan(board_state_before, objective)

#             if not action_plan.get("actionable", True):
#                 report_data['status'] = "Passed"
#                 report_data['actual_log'] = f"Solver correctly determined no action was possible. Board state was: {board_state_before}"
#                 report_data['actual_results'] = f"Board state remained unchanged, as expected. Reason: {action_plan.get('reason')}"
#             else:
#                 first_num, first_idx = action_plan['first_number'], action_plan['first_index']
#                 second_num, second_idx = action_plan['second_number'], action_plan['second_index']

#                 xpath1 = f"(//div[contains(@class, 'grid-cell') and not(contains(@class, 'blurred')) and not(contains(@class, 'cleared')) and normalize-space()='{first_num}'])[{first_idx}]"
#                 xpath2 = f"(//div[contains(@class, 'grid-cell') and not(contains(@class, 'blurred')) and not(contains(@class, 'cleared')) and normalize-space()='{second_num}'])[{second_idx}]"
                
#                 print(f"[DEBUG] Clicking based on plan: XPaths [{xpath1}] and [{xpath2}]")
#                 wait.until(EC.element_to_be_clickable((By.XPATH, xpath1))).click()
#                 time.sleep(0.5)
#                 wait.until(EC.element_to_be_clickable((By.XPATH, xpath2))).click()
                
#                 time.sleep(2)
#                 board_state_after = self._get_board_state(driver, wait)
#                 after_screenshot_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_after.png")
#                 driver.save_screenshot(after_screenshot_path)
#                 report_data["artifacts"]["screenshots"].append(os.path.basename(after_screenshot_path))

#                 report_data['status'] = "Pending Analysis"
#                 report_data['actual_log'] = f"Successfully clicked the pair: ({first_num}, {second_num}). Initial board state was: {board_state_before}"
#                 report_data['actual_results'] = f"Board after clicks: {board_state_after}."

#         except (TimeoutException, NoSuchElementException, IndexError) as e:
#             plan_str = f"the {action_plan.get('first_index', 'N/A')}-th instance of '{action_plan.get('first_number', 'N/A')}'"
#             error_message = f"Execution failed: Timed out trying to click {plan_str}. The Solver's plan may be invalid. The board state at the time of error was: {board_state_before}"
#             report_data['actual_log'] = error_message
#             report_data['actual_results'] = f"Could not complete action. The board state before the error was: {board_state_before}"
        
#         finally:
#             # --- This block now GUARANTEES logs and screenshots are saved ---
#             if driver:
#                 error_screenshot_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_final_state.png")
#                 driver.save_screenshot(error_screenshot_path)
#                 report_data["artifacts"]["screenshots"].append(os.path.basename(error_screenshot_path))
                
#                 print("ExecutorAgent: Closing session.")
#                 driver.quit()
            
#             # Save the report file no matter what
#             report_file_path = os.path.join(self.report_dir, f"test_case_{test_case_id}_report.json")
#             with open(report_file_path, "w") as report_file:
#                 json.dump(report_data, report_file, indent=4)
        
#         return report_data
#     # --- END OF REVERTED AND CORRECTED CODE ---