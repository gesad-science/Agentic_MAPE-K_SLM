class KnowledgeBase:
    def __init__(self):
        self.historical_base = []
        self.historical_analyses = []
        self.system_information = {}
        self.constraints = {}
        self.last_update = {}
        self.llm_settings = {}
        self.adaptation_goals = {}
        self.adaptation_options = {}
        self.plan_options = {}

    def get_history(self):
        return self.historical_base
    
    def update_history(self, data):
        self.historical_base.append(data)
    
    def update_analysis_history(self, data):
        self.historical_analyses.append(data)

    def get_last_monitor_output(self):
        """
        Retorna o último output registrado pelo Monitor.
        """
        for entry in reversed(self.historical_base):
            if entry["type"] == "monitor":
                return entry["data"]
        return None

    def get_last_analysis_output(self):
        """
        Retorna a última análise realizada pelo Analyzer.
        """
        for entry in reversed(self.historical_base):
            if entry["type"] == "analysis":
                return entry["data"]
        return None

knowledge_base = KnowledgeBase()
        