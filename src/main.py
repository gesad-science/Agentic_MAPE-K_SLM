import numpy as np
import json
import time

from crew import AnalyserCrew, PlannerCrew
from knowledgeBase import knowledge_base
from monitor.monitor import Monitor
from monitor.reader import CSVReader
from metrics_analyser import MetricsAnalyser
from executor import Executor


def convert_numpy(obj):
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [convert_numpy(v) for v in obj]

    if isinstance(obj, np.ndarray):
        return obj.tolist()

    if isinstance(obj, np.integer):
        return int(obj)

    if isinstance(obj, np.floating):
        return float(obj)

    if isinstance(obj, np.bool_):
        return bool(obj)

    return obj


class MAPEKExecutor:

    def __init__(self, csv_path: str):
        self.reader = CSVReader(csv_path)
        self.monitor = Monitor()
        self.knowledge = knowledge_base
        self.analyser = AnalyserCrew()
        self.metrics_analyser = MetricsAnalyser(self.knowledge)
        self.planner = PlannerCrew()
        self.executor = Executor(self.knowledge)

    def execute_step(self, current_state: dict | None):
        cycle_start_time = time.time()

        if current_state is None:
            # First step: read from the CSV file
            row = self.reader.next()
            if row is None:
                return None, True  # End of data

            # --------------------
            # MONITOR
            # --------------------
            print("\n--- Running Monitor ---")
            start_time = time.time()
            monitor_output = convert_numpy(
                self.monitor.process(row)
            )
            monitor_duration = time.time() - start_time
            print(f"Monitor finished in: {monitor_duration:.4f} seconds")
        else:
            print("--- Using state from previous cycle's execution. ---")
            # Subsequent steps: use the state from the previous cycle
            monitor_output = current_state

        print("Monitor input for this cycle:", json.dumps(monitor_output, indent=2, default=str))

        # --------------------
        # METRICS ANALYSER (part of Analyze)
        # --------------------
        print("\n--- Running Metrics Analyser ---")
        start_time = time.time()
        metrics_output = self.metrics_analyser.execute(monitor_output)
        metrics_analyser_duration = time.time() - start_time
        print(f"Metrics Analyser finished in: {metrics_analyser_duration:.4f} seconds")

        # --------------------
        # ANALYSER
        # --------------------
        print("\n--- Running Analyser Crew ---")
        start_time = time.time()
        analysis_crew_output = self.analyser.crew().kickoff(
            inputs={
                "monitor_output": monitor_output,
                "metrics_output": metrics_output
            }
        )
        analysis_output = json.loads(analysis_crew_output.raw)
        analyser_crew_duration = time.time() - start_time
        print(f"Analyser Crew finished in: {analyser_crew_duration:.4f} seconds")
        print("Analysis output:", json.dumps(analysis_output, indent=2, default=str))

        # --------------------
        # PLANNER
        # --------------------
        print("\n--- Running Planner Crew ---")
        start_time = time.time()
        plan_crew_output = self.planner.crew().kickoff(
            inputs={
                "analysis_output": json.dumps(analysis_output, indent=2)
            }
        )
        plan_output = json.loads(plan_crew_output.raw)
        planner_crew_duration = time.time() - start_time
        print(f"Planner Crew finished in: {planner_crew_duration:.4f} seconds")

        # --------------------
        # EXECUTE
        # --------------------
        print("\n--- Running Executor ---")
        start_time = time.time()
        # The executor takes the plan and the current state to produce the *next* state.
        next_state = self.executor.execute_plan(plan_output, monitor_output)
        executor_duration = time.time() - start_time
        print(f"Executor finished in: {executor_duration:.4f} seconds")

        # --------------------
        # UPDATE KNOWLEDGE BASE
        # --------------------
        self.knowledge.record_attempt(
            issue_type=analysis_output.get("issue_type"),
            tactic=plan_output.get("selected_strategy"),
            dist_before=monitor_output["metrics"]["dist_cube_target"],
            dist_after=next_state["metrics"]["dist_cube_target"]
        )
        self.knowledge.update_history(monitor_output)
        self.knowledge.update_analysis_history(analysis_output)

        cycle_duration = time.time() - cycle_start_time
        print(f"\n--- Total time for this cycle: {cycle_duration:.4f} seconds ---")

        # Check for termination condition
        if next_state['metrics']['dist_cube_target'] < self.knowledge.data['goal_threshold']:
            print("\n>>> GOAL REACHED! Terminating execution. <<<")
            # Include the final executed state in the return value
            return {
                "monitor": monitor_output, 
                "analysis": analysis_output, 
                "plan": plan_output, 
                "final_state": next_state
            }, True

        return next_state, False

    def execute(self):

        results = []
        current_state = None
        
        for i in range(10): # Limit to 10 steps to prevent infinite loops during testing
            print(f"\n\n--- MAPE-K Cycle {i+1} ---")
            result, done = self.execute_step(current_state)

            if done:
                if result:
                    results.append(result)
                break

            current_state = result
            results.append(result)

            print("=" * 60)
            print("END OF CYCLE REPORT")
        
        return results
    
    def get_knowledge_base(self):
        return self.knowledge
    
executor = MAPEKExecutor(
    "data/caminho-obstaculo-grande.csv"
)

results = executor.execute()
