import numpy as np

from crew import AnalyserCrew
from knowledgeBase import knowledge_base
from monitor.monitor import Monitor
from monitor.reader import CSVReader


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

    def execute_step(self):

        row = self.reader.next()

        if row is None:
            return None

        # --------------------
        # MONITOR
        # --------------------
        monitor_output = convert_numpy(
            self.monitor.process(row)
        )

        # --------------------
        # ANALYSER
        # --------------------
        analysis_output = self.analyser.crew().kickoff(
            inputs={
                "monitor_output": monitor_output
            }
        )

        # --------------------
        # UPDATE KNOWLEDGE BASE
        # --------------------
        self.knowledge. update_history(
            monitor_output
        )

        self.knowledge.update_analysis_history(
            analysis_output
        )

        return {
            "monitor": monitor_output,
            "analysis": analysis_output
        }

    def execute(self):

        results = []

        while True:

            result = self.execute_step()

            if result is None:
                break

            results.append(result)

            print("=" * 60)
            print("MONITOR")
            print(result["monitor"])
            print()

            print("ANALYSIS")
            print(result["analysis"])

        return results
    
    def get_knowledge_base(self):
        return self.knowledge
    
executor = MAPEKExecutor(
    "data/caminho-obstaculo-conhecido.csv"
)

results = executor.execute()


