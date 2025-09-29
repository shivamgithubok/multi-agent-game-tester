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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Initializing agents...")
planner_agent = PlannerAgent()
ranker_agent = RankerAgent()
solver_agent = SolverAgent()
executor_agent = ExecutorAgent(solver=solver_agent) 
analyzer_agent = AnalyzerAgent()
orchestrator_agent = OrchestratorAgent(planner_agent, ranker_agent, executor_agent, analyzer_agent)
print("All agents initialized.")

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
    
    default_context = "No past failures recorded."
    if os.path.exists("test_memory.log"):
        with open("test_memory.log", "r") as f:
            default_context = f.read()

    human_guidance = "No specific guidance provided."
    if os.path.exists("human_guidance.txt"):
        with open("human_guidance.txt", "r") as f:
            human_guidance = f.read()
    
    _generated_test_cases = planner_agent.generate_test_cases(
        context=default_context, 
        human_guidance=human_guidance
    )
    return {"test_cases": _generated_test_cases}

# --- START OF FIX ---
@app.post("/execute_test_case/{test_case_id}")
async def execute_test_case(test_case_id: int):
    global _generated_test_cases
    if not _generated_test_cases or test_case_id < 1 or test_case_id > len(_generated_test_cases):
        raise HTTPException(status_code=404, detail="Test case not found.")
    
    test_case_to_execute = _generated_test_cases[test_case_id - 1]
    
    # Define a default resolution for this single-run endpoint.
    default_resolution = (1920, 1080) # Standard Desktop
    
    # Call the executor with BOTH required arguments.
    result = executor_agent.execute_test_case(
        test_case=test_case_to_execute, 
        resolution=default_resolution
    )
    
    # It's also good practice to analyze the result for a complete report.
    analyzed_result = analyzer_agent.analyze_test_case(result)
    return analyzed_result
# --- END OF FIX ---

@app.get("/get_report/{test_case_id}")
async def get_report(test_case_id: int):
    # This might need to be adjusted if reports are named with resolutions
    report_file_path = os.path.join("report", f"test_case_{test_case_id}_Desktop_report.json") # Assume Desktop for single report fetch
    if not os.path.exists(report_file_path):
        raise HTTPException(status_code=404, detail="Report file not found. Check for other resolutions.")
    
    with open(report_file_path, "r") as report_file:
        report = json.load(report_file)
    return {"report": report}

@app.post("/orchestrate_tests")
async def orchestrate_tests():
    results = orchestrator_agent.orchestrate()
    return {"results": results}