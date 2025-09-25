from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.analyzer import AnalyzerAgent
from agents.orchestrator import OrchestratorAgent
from agents.ranker import RankerAgent
import json
import os

app = FastAPI()

# Create agent instances
planner_agent = PlannerAgent()
ranker_agent = RankerAgent()
executor_agent = ExecutorAgent()
analyzer_agent = AnalyzerAgent()
orchestrator_agent = OrchestratorAgent(planner_agent, ranker_agent, executor_agent, analyzer_agent)

# Global variable to store generated test cases
_generated_test_cases = []

# Define static file serving for logs and screenshots


@app.get("/report/{file_name}")
async def get_file(file_name: str):
    file_path = os.path.join("report", file_name)
    if os.path.exists(file_path):
        return FileResponse(file_path)  # FastAPI serves the binary PNG file correctly
    else:
        raise HTTPException(status_code=404, detail="File not found")
    
@app.get("/generate_test_cases")
async def generate_test_cases():
    global _generated_test_cases
    _generated_test_cases = planner_agent.generate_test_cases()
    return {"test_cases": _generated_test_cases}

@app.post("/execute_test_case/{test_case_id}")
async def execute_test_case(test_case_id: int):
    global _generated_test_cases
    if not _generated_test_cases or test_case_id < 1 or test_case_id > len(_generated_test_cases):
        raise HTTPException(status_code=404, detail="Test case not found or not generated yet.")
    
    # Retrieve the full test case object
    test_case_to_execute = _generated_test_cases[test_case_id - 1]
    result = executor_agent.execute_test_case(test_case_to_execute)
    return result


@app.get("/get_report/{test_case_id}")
async def get_report(test_case_id: int):
    # Path to the report file
    log_file_path = os.path.join("report", f"test_case_{test_case_id}_report.json")
    
    # Check if the report file exists
    if not os.path.exists(log_file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    # Read and return the JSON report content
    try:
        with open(log_file_path, "r") as log_file:
            report = json.load(log_file)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Error decoding the JSON report file")
    
    return {"report": report}

@app.post("/orchestrate_tests")
async def orchestrate_tests():
    results = orchestrator_agent.orchestrate()
    return {"results": results}