import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.docstore.document import Document

class OrchestratorAgent:
    def __init__(self, planner, ranker, executor, analyzer):
        self.planner = planner
        self.ranker = ranker
        self.executor = executor
        self.analyzer = analyzer
        
        # --- START OF RAG IMPLEMENTATION ---
        self.guidance_file = "human_guidance.txt"
        self.vector_store_path = "faiss_memory_index"
        
        # Initialize the local embedding model from Hugging Face
        print("Orchestrator: Initializing embedding model (all-MiniLM-L6-v2)...")
        self.embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        
        # Load the FAISS vector database from disk, or create it if it doesn't exist
        if os.path.exists(self.vector_store_path):
            print(f"Orchestrator: Loading existing memory from '{self.vector_store_path}'...")
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embedding_model, allow_dangerous_deserialization=True)
        else:
            print(f"Orchestrator: No memory found. Creating new vector store at '{self.vector_store_path}'...")
            # We need to create an index with at least one document
            initial_text = "This is the beginning of the test agent's memory."
            self.vector_store = FAISS.from_texts([initial_text], self.embedding_model)
        # --- END OF RAG IMPLEMENTATION ---

    def orchestrate(self):
        try:
            # --- RAG: RETRIEVAL STEP ---
            print("\n--- Step 1: Retrieving Context from Memory (Vector DB) ---")
            # Perform a similarity search on the vector DB to find relevant past failures
            retriever = self.vector_store.as_retriever()
            past_failures = retriever.invoke("Past test case failures, errors, and objectives")
            context = "\n".join([doc.page_content for doc in past_failures])
            print(f"Orchestrator: Retrieved context:\n{context}")

            human_guidance = "No specific guidance provided."
            if os.path.exists(self.guidance_file):
                with open(self.guidance_file, "r") as f: human_guidance = f.read()

            print("\n--- Step 2: Defining Foundational & AI-Generated Tests ---")
            foundational_objectives = [
                {'id': 101, 'test_objective': "Verify the core game mechanic: successfully remove a valid pair that sums to 10.", 'expected_results': "The two numbers summing to 10 should be removed."},
                {'id': 102, 'test_objective': "Verify the core game mechanic: successfully remove a valid identical pair.", 'expected_results': "The two identical numbers should be removed."}
            ]
            ai_generated_cases = self.planner.generate_test_cases(context=context, human_guidance=human_guidance)
            all_test_cases = foundational_objectives + (ai_generated_cases if ai_generated_cases else [])

            print("\n--- Step 3: Ranking All Test Objectives ---")
            ranked_test_cases = self.ranker.rank_test_cases(all_test_cases)
            
            print(f"\n--- Step 4: Executing Top {len(ranked_test_cases)} Objectives ---")
            results = []
            resolutions = {"Desktop": (1280, 1024), "Mobile": (390, 844)}
            for resolution_name, resolution_size in resolutions.items():
                print(f"\n--- TESTING ON RESOLUTION: {resolution_name} ---")
                for test_case in ranked_test_cases:
                    executed_report = self.executor.execute_test_case(test_case, resolution=resolution_size)
                    executed_report['resolution_name'] = resolution_name
                    analyzed_report = self.analyzer.analyze_test_case(executed_report)
                    results.append(analyzed_report)
            
            # --- RAG: INGESTION / LEARNING STEP ---
            print("\n--- Step 5: Learning from Failures and Updating Memory ---")
            new_failures_to_learn = []
            for report in results:
                if report.get('status') == 'Failed':
                    # Create a detailed text document for the failure
                    failure_content = (
                        f"Failure Report for Test Case ID {report['test_case_id']} on {report['resolution_name']}:\n"
                        f"Objective: {report['objective']}\n"
                        f"Expected Results: {report['expected_results']}\n"
                        f"Actual Log: {report['actual_log']}\n"
                        f"Actual Results: {report['actual_results']}\n"
                    )
                    # Create metadata linking the text to the screenshot evidence
                    failure_metadata = {
                        "test_case_id": report['test_case_id'],
                        "resolution": report['resolution_name'],
                        "screenshots": report['artifacts']['screenshots']
                    }
                    new_failures_to_learn.append(Document(page_content=failure_content, metadata=failure_metadata))

            if new_failures_to_learn:
                print(f"Found {len(new_failures_to_learn)} new failures. Embedding and adding to vector store...")
                self.vector_store.add_documents(new_failures_to_learn)
                # Save the updated index to disk for the next run
                self.vector_store.save_local(self.vector_store_path)
                print("Memory updated successfully.")
            else:
                print("No new failures to learn from on this run.")

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