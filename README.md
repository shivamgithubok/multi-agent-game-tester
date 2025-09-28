I have used FAST api preferetd to test it insted for frontend for more clear visulization .
RUN:-
#### localhost:8001/docs


# Multi-Agent Game Tester

A proof-of-concept automated testing system for web-based math puzzle games using multiple AI agents and LangChain integration.

## Features

- 🤖 Multi-agent architecture for comprehensive test coverage
- 🎮 Automated testing of web-based math puzzle games
- 📊 Generate and execute 20+ test cases automatically
- 📸 Capture test artifacts (screenshots, DOM snapshots, console logs)
- 📝 Detailed test reports with validation results
- 🌐 FastAPI backend with modern web frontend

## Architecture

- **PlannerAgent**: Generates test cases using Google's Gemini AI
- **RankerAgent**: Prioritizes and selects top test cases
- **ExecutorAgent**: Runs the tests and captures artifacts
- **OrchestratorAgent**: Coordinates test execution
- **AnalyzerAgent**: Validates results and generates reports

## Prerequisites

- Python 3.8+
- Node.js 14+
- Google Gemini API key

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/multi-agent-game-tester.git
cd multi-agent-game-tester

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
copy .env.example .env
# Edit .env with your Gemini API key
```

## Running the Application

```bash
# Start the backend server
cd backend
uvicorn main:app --reload

# Open frontend/index.html in your browser
start frontend/index.html
```

## Project Structure

```
multi-agent-game-tester/
├── backend/
│   ├── main.py
│   ├── agents/
│   │   ├── planner.py
│   │   ├── ranker.py
│   │   ├── executor.py
│   │   ├── orchestrator.py
│   │   └── analyzer.py
│   └── utils/
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── tests/
├── requirements.txt
└── README.md
```