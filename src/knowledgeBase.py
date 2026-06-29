class KnowledgeBase:
    def __init__(self):
        self.historical_base = []
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

        