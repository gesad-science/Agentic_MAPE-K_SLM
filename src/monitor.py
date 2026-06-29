from knowledgeBase import KnowledgeBase

class Monitor:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.knowledge_base = knowledge_base
        self.metrics = {}
        self.update()
    
    def get_metrics(self):
        return f"Metrics={self.metrics}"

    def update(self):
        self.knowledge_base.update_history(self.get_metrics)

    