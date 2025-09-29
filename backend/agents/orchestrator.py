import os

class OrchestratorAgent:
    def __init__(self, planner, ranker, executor, analyzer):
        self.planner = planner
        self.ranker = ranker
        self.executor = executor
        self.analyzer = analyzer
        self.memory_file = "test_memory.log"
        self.guidance_file = "human_guidance.txt"

    def orchestrate(self):
        try:
            # --- LAYER 1: FOUNDATIONAL INTELLIGENCE ("The Mind") ---
            print("\n--- Step 1: Defining Foundational & Multi-Resolution Tests ---")
            foundational_objectives = [
                {'id': 1, 'test_objective': "Verify the core game mechanic: successfully remove a valid pair that sums to 10.", 'expected_results': "The two numbers summing to 10 should be removed from the grid."},
                {'id': 2, 'test_objective': "Verify the core game mechanic: successfully remove a valid identical pair.", 'expected_results': "The two identical numbers should be removed from the grid."},
                {'id': 3, 'test_objective': "Verify the core negative case: an invalid pair (e.g., summing to 9) cannot be removed.", 'expected_results': "The numbers should remain on the board, and no pair should be cleared."}
            ]
            resolutions = {
                "Desktop": (720, 1080),
                "Mobile": (390, 844)
            }

            # --- LAYER 2: TEACHABLE INTELLIGENCE (Human Guidance) ---
            print("\n--- Step 2: Retrieving Memory (RAG) and Human Guidance ---")
            context = "No past failures recorded."
            if os.path.exists(self.memory_file):
                with open(self.memory_file, "r") as f: context = f.read()

            human_guidance = "No specific guidance provided. Focus on general test coverage."
            if os.path.exists(self.guidance_file):
                with open(self.guidance_file, "r") as f: human_guidance = f.read()

            # --- LAYER 3: CREATIVE INTELLIGENCE (AI Exploration) ---
            print("\n--- Step 3: Generating AI Test Objectives with Guidance ---")
            ai_generated_cases = self.planner.generate_test_cases(context=context, human_guidance=human_guidance)
            
            # Combine the foundational "mind" with the AI's creativity
            all_test_cases = foundational_objectives + (ai_generated_cases)

            print("\n--- Step 4: Ranking All Test Objectives ---")
            ranked_test_cases = self.ranker.rank_test_cases(all_test_cases)
            
            print(f"\n--- Step 5: Executing Top {len(ranked_test_cases)} Objectives Across {len(resolutions)} Resolutions ---")
            results = []
            for resolution_name, resolution_size in resolutions.items():
                print(f"\n--- TESTING ON RESOLUTION: {resolution_name} ({resolution_size[0]}x{resolution_size[1]}) ---")
                for test_case in ranked_test_cases:
                    executed_report = self.executor.execute_test_case(test_case, resolution=resolution_size)
                    executed_report['resolution_name'] = resolution_name
                    analyzed_report = self.analyzer.analyze_test_case(executed_report)
                    results.append(analyzed_report)
            
            print("\n--- Step 6: Learning from Failures ---")
            failed_summaries = [f"- Objective: \"{r['objective']}\" on {r['resolution_name']}\n  - Log: {r['actual_log']}\n" for r in results if r.get('status') == 'Failed']
            if failed_summaries:
                print(f"Found {len(failed_summaries)} failures. Updating memory.")
                with open(self.memory_file, "a") as f: f.write("\n--- New Failures ---\n" + "\n".join(failed_summaries))

            print("\n--- Orchestration Complete ---")
            return results

        except Exception as e:
            print(f"A critical error occurred during orchestration: {e}")
            return {"error": str(e), "results": []}

# import os

# class OrchestratorAgent:
#     def __init__(self, planner, ranker, executor, analyzer):
#         self.planner = planner
#         self.ranker = ranker
#         self.executor = executor
#         self.analyzer = analyzer
#         self.memory_file = "test_memory.log"

#     def orchestrate(self):
#         try:
#             # --- RAG: RETRIEVAL STEP ---
#             print("\n--- Step 1: Retrieving Past Test Results (Memory) ---")
#             context = "No past failures recorded."
#             if os.path.exists(self.memory_file):
#                 with open(self.memory_file, "r") as f:
#                     context = f.read()
            
#             # --- RAG: AUGMENTED GENERATION STEP ---
#             print("\n--- Step 2: Generating Test Objectives with Context ---")
#             all_test_cases = self.planner.generate_test_cases(context=context)
#             if not all_test_cases:
#                 raise Exception("Planner failed to generate test cases.")
            
#             print("\n--- Step 3: Ranking Test Objectives ---")
#             ranked_test_cases = self.ranker.rank_test_cases(all_test_cases)
#             if not ranked_test_cases:
#                 raise Exception("Ranker failed to select test cases.")
            
#             print(f"\n--- Step 4: Executing and Analyzing Top {len(ranked_test_cases)} Objectives ---")
#             results = []
#             for test_case in ranked_test_cases:
#                 executed_report = self.executor.execute_test_case(test_case)
#                 analyzed_report = self.analyzer.analyze_test_case(executed_report)
#                 results.append(analyzed_report)
            
#             # --- RAG: MEMORY CREATION STEP ---
#             print("\n--- Step 5: Learning from Failures ---")
#             failed_summaries = []
#             for report in results:
#                 if report.get('status') == 'Failed':
#                     summary = (f"- Objective: \"{report['objective']}\"\n"
#                                f"  - Failure Log: {report['actual_log']}\n")
#                     failed_summaries.append(summary)

#             if failed_summaries:
#                 print(f"Found {len(failed_summaries)} failures. Appending to memory.")
#                 with open(self.memory_file, "a") as f:
#                     f.write("\n--- New Failures ---\n")
#                     f.write("\n".join(failed_summaries))
#             else:
#                 print("No new failures to learn from on this run.")

#             print("\n--- Orchestration Complete ---")
#             return results

#         except Exception as e:
#             print(f"A critical error occurred during orchestration: {e}")
#             return {"error": str(e), "results": []}