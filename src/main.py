from itertools import count

from crew import AnalyserCrew
from monitor.reader import CSVReader
from monitor.monitor import Monitor
import numpy as np


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


csv_reader = CSVReader("src/data/caminho-feliz.csv")
monitor_instance = Monitor()
crew = AnalyserCrew().crew()
count=0
outputs = []
aux=True
while aux:
    row = csv_reader.next()

    if row is None:
        break

    output = monitor_instance.process(row)
    result = crew.kickoff(
        inputs={
            "monitor_output": convert_numpy(output)
        }
    )
    print(result)
    if count==8:
        aux = False
    
    count+=1
    outputs.append(convert_numpy(output))


