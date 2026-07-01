from monitor import reader
from monitor import monitor

reader = reader.CSVReader("data/caminho-feliz.csv")
monitor = monitor.Monitor()

while True:
    row = reader.next()

    if row is None:
        break

    output = monitor.process(row)
    print(output)