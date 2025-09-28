document.getElementById("generate-btn").addEventListener("click", generateTestCases);
document.getElementById("orchestrate-btn").addEventListener("click", orchestrateTests);

async function generateTestCases() {
  const generateBtn = document.getElementById("generate-btn");
  const orchestrateBtn = document.getElementById("orchestrate-btn");

  generateBtn.disabled = true;
  orchestrateBtn.disabled = true;
  document.getElementById("loading-indicator").classList.remove("hidden");
  document.getElementById("execution-status").textContent = ''; // Clear previous status
  document.getElementById("report-content").innerHTML = ''; // Clear previous report

  try {
    const response = await fetch("http://127.0.0.1:8001/generate_test_cases", {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      mode: 'cors'
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    document.getElementById("loading-indicator").classList.add("hidden");
    generateBtn.disabled = false;
    orchestrateBtn.disabled = false;

    const testCasesList = document.getElementById("test-cases-list");
    testCasesList.innerHTML = '';
    
    console.log("Received data:", data);

    // Fix: Access the test_cases array from the response
    const testCases = data.test_cases;

    // Check if test_cases exists and is an array
    if (!testCases || !Array.isArray(testCases)) {
      testCasesList.innerHTML = "<li class='list-group-item'>Invalid response format</li>";
      return;
    }

    // Update the test case rendering to handle object format
    testCases.forEach((testCase, index) => {
      const li = document.createElement("li");
      li.className = 'list-group-item';
      
      // Handle test case data as an object instead of string
      const title = testCase.objective || testCase.title || 'N/A';
      const description = [
        `Test ID: ${testCase.id || index + 1}`,
        `Description: ${testCase.description || 'N/A'}`,
        `Initial State: ${testCase.initial_state || 'N/A'}`,
        `Expected Actions: ${testCase.expected_actions || 'N/A'}`,
        `Expected Results: ${testCase.expected_results || 'N/A'}`
      ].join('\n');
      
      li.innerHTML = `
        <div class="test-case-summary">
          <strong>Test Case ${index + 1}:</strong> 
          <span class="test-title">${title}</span>
          <button class="btn btn-sm btn-info toggle-details">Show Details</button>
        </div>
        <div class="test-case-details hidden">
          <pre class="test-description mt-2">${description}</pre>
          <div class="mt-2">
            <button class="btn btn-sm btn-primary execute-single-btn" 
                    data-id="${testCase.id || index + 1}">
              Execute This Test
            </button>
          </div>
        </div>
      `;
      testCasesList.appendChild(li);
    });

    // Add success message
    document.getElementById("execution-status").innerHTML = `
      <div class="alert alert-success">
        Successfully generated ${testCases.length} test cases.
      </div>
    `;

    // Add event listener for toggling test case details
    testCasesList.addEventListener("click", function(event) {
      if (event.target.classList.contains("toggle-details")) {
        const detailsDiv = event.target.closest(".test-case-summary").nextElementSibling;
        detailsDiv.classList.toggle("hidden");
        event.target.textContent = detailsDiv.classList.contains("hidden") ? "Show Details" : "Hide Details";
      }
    });
  } catch (error) {
    console.error("Error generating test cases:", error);
    document.getElementById("loading-indicator").classList.add("hidden");
    generateBtn.disabled = false;
    orchestrateBtn.disabled = false;
    document.getElementById("execution-status").innerHTML = `
      <div class="alert alert-danger">
        Error generating test cases: ${error.message}
      </div>
    `;
  }
}

// Add event listener for executing test cases
document.getElementById("test-cases-list").addEventListener("click", async function (event) {
  // Handle execute single test button click
  if (event.target.classList.contains("execute-single-btn")) {
    const testCaseId = event.target.dataset.id;
    await executeTestCase(testCaseId);
  }
  // Previous logic for clicking on the LI itself is no longer needed/desired
});

async function executeTestCase(testCaseId) {
  const executeButtons = document.querySelectorAll(".execute-single-btn");
  const generateBtn = document.getElementById("generate-btn");
  const orchestrateBtn = document.getElementById("orchestrate-btn");

  executeButtons.forEach(btn => btn.disabled = true);
  generateBtn.disabled = true;
  orchestrateBtn.disabled = true;
  document.getElementById("execution-status").textContent = `Executing Test Case ${testCaseId}...`;
  document.getElementById("report-content").innerHTML = ''; // Clear previous reports

  try {
    const response = await fetch(`http://127.0.0.1:8000/execute_test_case/${testCaseId}`, {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const result = await response.json();

    executeButtons.forEach(btn => btn.disabled = false);
    generateBtn.disabled = false;
    orchestrateBtn.disabled = false;

    document.getElementById("execution-status").textContent = `Test Case ${testCaseId} Result: ${result.status} (Verdict: ${result.analysis?.verdict || 'N/A'})`;

    // Fetch and display the report after execution
    const reportResponse = await fetch(`http://127.0.0.1:8000/get_report/${testCaseId}`);
    if (!reportResponse.ok) {
        throw new Error(`HTTP error! status: ${reportResponse.status}`);
    }
    const reportData = await reportResponse.json();
    displayReport(testCaseId, reportData.report); // Use the new displayReport function
      
  } catch (error) {
    console.error("Error executing test case:", error);
    executeButtons.forEach(btn => btn.disabled = false);
    generateBtn.disabled = false;
    orchestrateBtn.disabled = false;
    document.getElementById("execution-status").textContent = `Error executing Test Case ${testCaseId}: ${error.message}.`;
  }
}

async function orchestrateTests() {
  const generateBtn = document.getElementById("generate-btn");
  const orchestrateBtn = document.getElementById("orchestrate-btn");

  generateBtn.disabled = true;
  orchestrateBtn.disabled = true;
  document.getElementById("loading-indicator").classList.remove("hidden");
  document.getElementById("test-cases-list").innerHTML = ''; // Clear previous test cases
  document.getElementById("execution-status").textContent = 'Orchestrating all tests...';
  document.getElementById("report-content").innerHTML = ''; // Clear previous report

  try {
    const response = await fetch("http://127.0.0.1:8000/orchestrate_tests", {
      method: 'POST'
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();

    document.getElementById("loading-indicator").classList.add("hidden");
    generateBtn.disabled = false;
    orchestrateBtn.disabled = false;

    const testCasesList = document.getElementById("test-cases-list");
    testCasesList.innerHTML = '';

    if (data.results && data.results.length > 0) {
      data.results.forEach(report => {
        const li = document.createElement("li");
        li.innerHTML = `
          <div class="test-case-summary">
            <strong>Test Case ${report.test_case_id}:</strong> ${report.objective || 'N/A'} - Status: ${report.status} (Verdict: ${report.analysis.verdict || 'N/A'})
            <button class="toggle-details">Show Details</button>
          </div>
          <div class="test-case-details hidden">
            <p><strong>Initial State:</strong> ${report.initial_state || 'N/A'}</p>
            <p><strong>Expected Actions:</strong> ${report.expected_actions || 'N/A'}</p>
            <p><strong>Expected Results:</strong> ${report.expected_results || 'N/A'}</p>
            <p><strong>Reason:</strong> ${report.analysis.reason || 'N/A'}</p>
            <p><strong>Actual Log:</strong> ${report.actual_log || 'N/A'}</p>
            <p><strong>Screenshot:</strong> <img src="http://127.0.0.1:8000/report/test_case_${report.test_case_id}_screenshot.png" alt="Screenshot" width="200"></p>
            <p><strong>Log File:</strong> <a href="http://127.0.0.1:8000/report/test_case_${report.test_case_id}_log.txt" target="_blank">Download Log</a></p>
          </div>
        `;
        testCasesList.appendChild(li);

        // No longer calling displayReport here to avoid duplicate display and to keep orchestrated results in the list
      });

      // Add event listener for toggling test case details for orchestrated results
      testCasesList.addEventListener("click", function(event) {
        if (event.target.classList.contains("toggle-details")) {
          const detailsDiv = event.target.closest(".test-case-summary").nextElementSibling;
          detailsDiv.classList.toggle("hidden");
          event.target.textContent = detailsDiv.classList.contains("hidden") ? "Show Details" : "Hide Details";
        }
      });

      document.getElementById("execution-status").textContent = `Orchestration completed for ${data.results.length} test cases.`;
    } else {
      testCasesList.innerHTML = "<li>No orchestrated test results.</li>";
      document.getElementById("execution-status").textContent = "Orchestration completed, but no test results were returned.";
    }

  } catch (error) {
    console.error("Error orchestrating tests:", error);
    document.getElementById("loading-indicator").classList.add("hidden");
    generateBtn.disabled = false;
    orchestrateBtn.disabled = false;
    document.getElementById("execution-status").textContent = `Error during orchestration: ${error.message}`;
  }
}

function displayReport(testCaseId, reportData) {
    const reportContent = document.getElementById("report-content");
    const reportDiv = document.createElement("div");
    reportDiv.innerHTML = `
        <h3>Report for Test Case ${testCaseId}</h3>
        <p><strong>Status:</strong> ${reportData.status}</p>
        <p><strong>Verdict:</strong> ${reportData.analysis.verdict || 'N/A'}</p>
        <p><strong>Reason:</strong> ${reportData.analysis.reason || 'N/A'}</p>
        <p><strong>Objective:</strong> ${reportData.objective || 'N/A'}</p>
        <p><strong>Initial State:</strong> ${reportData.initial_state || 'N/A'}</p>
        <p><strong>Expected Actions:</strong> ${reportData.expected_actions || 'N/A'}</p>
        <p><strong>Expected Results:</strong> ${reportData.expected_results || 'N/A'}</p>
        <h4>Artifacts:</h4>
        <p><strong>Screenshot:</strong> <img src="http://127.0.0.1:8000/report/test_case_${testCaseId}_screenshot.png" alt="Screenshot" width="300"></p>
        <p><strong>Log:</strong> <a href="http://127.00.0.1:8000/report/test_case_${testCaseId}_log.txt" target="_blank">Download Log</a></p>
        <hr>
    `;
    reportContent.appendChild(reportDiv);
}

// Add some CSS styles for better formatting
const style = document.createElement('style');
style.textContent = `
  .test-title {
    font-weight: normal;
    margin-left: 10px;
    flex-grow: 1;
  }
  
  .test-description {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 4px;
    white-space: pre-wrap;
    font-family: monospace;
  }
  
  .test-case-summary {
    display: flex;
    align-items: center;
    gap: 10px;
  }
`;
document.head.appendChild(style);
