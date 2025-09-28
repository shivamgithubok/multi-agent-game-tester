class OrchestratorAgent:
    def __init__(self, planner, ranker, executor, analyzer):
        self.planner = planner
        self.ranker = ranker
        self.executor = executor
        self.analyzer = analyzer

    def orchestrate(self):
        # --- START OF NEW ORCHESTRATION LOGIC ---
        driver, wait = None, None  # Initialize driver to None
        try:
            # Step 1: Perform one-time browser setup
            print("\n--- Step 1: Setting Up Browser Session ---")
            driver, wait = self.executor.setup()

            # Step 2: Generate test objectives
            print("\n--- Step 2: Generating Test Objectives ---")
            all_test_cases = self.planner.generate_test_cases()
            if not all_test_cases:
                raise Exception("Planner failed to generate test cases.")
            
            # Step 3: Rank and select the top 10 objectives
            print("\n--- Step 3: Ranking Test Objectives ---")
            ranked_test_cases = self.ranker.rank_test_cases(all_test_cases)
            if not ranked_test_cases:
                raise Exception("Ranker failed to select test cases.")
            
            # Step 4: Execute and analyze the top 10 tests IN A LOOP on the SAME browser
            print(f"\n--- Step 4: Executing and Analyzing Top {len(ranked_test_cases)} Objectives ---")
            results = []
            for test_case in ranked_test_cases:
                # Pass the existing driver and wait objects to the test runner
                executed_report = self.executor.run_single_test(driver, wait, test_case)
                analyzed_report = self.analyzer.analyze_test_case(executed_report)
                results.append(analyzed_report)
            
            print("\n--- Orchestration Complete ---")
            return results

        except Exception as e:
            print(f"An error occurred during orchestration: {e}")
            return {"error": str(e)}

        finally:
            # Step 5: Ensure the browser is closed, no matter what happens
            if driver:
                self.executor.teardown(driver)
        # --- END OF NEW ORCHESTRATION LOGIC ---