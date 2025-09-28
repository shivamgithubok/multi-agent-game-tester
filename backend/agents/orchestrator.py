class OrchestratorAgent:
    def __init__(self, planner, ranker, executor, analyzer):
        self.planner = planner
        self.ranker = ranker
        self.executor = executor
        self.analyzer = analyzer

    def orchestrate(self):
        try:
            # Step 1: Generate test objectives
            print("\n--- Step 1: Generating Test Objectives ---")
            all_test_cases = self.planner.generate_test_cases()
            if not all_test_cases:
                raise Exception("Planner failed to generate test cases.")
            
            # Step 2: Rank and select the top 10 objectives
            print("\n--- Step 2: Ranking Test Objectives ---")
            ranked_test_cases = self.ranker.rank_test_cases(all_test_cases)
            if not ranked_test_cases:
                raise Exception("Ranker failed to select test cases.")
            
            # Step 3: Execute and analyze the top 10 tests in a simple loop
            print(f"\n--- Step 3: Executing and Analyzing Top {len(ranked_test_cases)} Objectives ---")
            results = []
            for test_case in ranked_test_cases:
                # The executor now handles its own setup and teardown for each test case.
                # The orchestrator's only job is to call it.
                executed_report = self.executor.execute_test_case(test_case)
                analyzed_report = self.analyzer.analyze_test_case(executed_report)
                results.append(analyzed_report)
            
            print("\n--- Orchestration Complete ---")
            return results

        except Exception as e:
            print(f"A critical error occurred during orchestration: {e}")
            # Ensure a dictionary is returned for JSON compatibility
            return {"error": str(e), "results": []} 
        # --- END OF CORRECTED ORCHESTRATION LOGIC ---