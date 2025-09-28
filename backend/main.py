from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.analyzer import AnalyzerAgent
from agents.orchestrator import OrchestratorAgent
from agents.ranker import RankerAgent
from agents.solver import SolverAgent
import json
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],  # Add your frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Agent setup is correct
print("Initializing agents...")
planner_agent = PlannerAgent()
ranker_agent = RankerAgent()
solver_agent = SolverAgent()
executor_agent = ExecutorAgent(solver=solver_agent) 
analyzer_agent = AnalyzerAgent()
orchestrator_agent = OrchestratorAgent(planner_agent, ranker_agent, executor_agent, analyzer_agent)
print("All agents initialized.")

# ... (other endpoints like /report and /generate_test_cases are fine) ...
@app.get("/report/{file_name}")
async def get_file(file_name: str):
    file_path = os.path.join("report", file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

_generated_test_cases = []

@app.get("/generate_test_cases")
async def generate_test_cases():
    global _generated_test_cases
    _generated_test_cases = planner_agent.generate_test_cases()
    return {"test_cases": _generated_test_cases}


# --- REVERTED TO SIMPLER LOGIC ---
@app.post("/execute_test_case/{test_case_id}")
async def execute_test_case(test_case_id: int):
    global _generated_test_cases
    if not _generated_test_cases or test_case_id < 1 or test_case_id > len(_generated_test_cases):
        raise HTTPException(status_code=404, detail="Test case not found.")
    
    test_case_to_execute = _generated_test_cases[test_case_id - 1]
    
    # The executor now handles its own lifecycle. This is much cleaner.
    result = executor_agent.execute_test_case(test_case_to_execute)
    return result
# --- END OF REVERTED LOGIC ---

@app.get("/get_report/{test_case_id}")
async def get_report(test_case_id: int):
    report_file_path = os.path.join("report", f"test_case_{test_case_id}_report.json")
    if not os.path.exists(report_file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    with open(report_file_path, "r") as report_file:
        report = json.load(report_file)
    return {"report": report}

@app.post("/orchestrate_tests")
async def orchestrate_tests():
    results = orchestrator_agent.orchestrate()
    return {"results": results}