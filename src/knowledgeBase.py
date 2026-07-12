class KnowledgeBase:
    def __init__(self):
        self.historical_base = []
        self.historical_analyses = []
        self.session_attempts = []  # NEW: Current session history
        self.data = {
            "goal_threshold": 0.05,
            "allowed_tasks": ["PUSH", "PICK_AND_PLACE", "REACH", "HOLD"],
            "available_scripts": ["script_1", "reach_only", "left_right"],
            "policies": {
                "goal_not_reached_yet": {
                    "preferred": [
                        "continue_push",
                        "switch_to_pick_and_place",
                        "switch_to_reach"
                    ]
                },
                "path_blocked": {
                    "preferred": [
                        "switch_to_pick_and_place",
                        "activate_script_left_right"
                    ]
                },
                "goal_reached": {
                    "preferred": ["hold_position"]
                }
            },
            "adaptation_history": [
                {
                    "issue_type": "goal_not_reached_yet",
                    "strategy": "continue_push",
                    "success_rate": 0.84,
                    "cost": 0.20,
                },
                {
                    "issue_type": "goal_not_reached_yet",
                    "strategy": "switch_to_pick_and_place",
                    "success_rate": 0.79,
                    "cost": 0.55,
                },
                {
                    "issue_type": "path_blocked",
                    "strategy": "switch_to_pick_and_place",
                    "success_rate": 0.91,
                    "cost": 0.62,
                },
                {
                    "issue_type": "path_blocked",
                    "strategy": "activate_script_left_right",
                    "success_rate": 0.58,
                    "cost": 0.35,
                },
            ],
        }
        self.system_information = {}
        self.constraints = {}
        self.last_update = {}
        self.llm_settings = {}
        self.adaptation_goals = {}
        self.adaptation_options = {}
        self.plan_options = {}

    def get_history(self):
        return self.historical_base
    
    def record_attempt(self, issue_type: str, tactic: str, dist_before: float, dist_after: float):
        """Records the outcome of a tactic within the current session."""
        if not all([issue_type, tactic, dist_before is not None, dist_after is not None]):
            return # Avoid recording incomplete data
            
        progress = round(dist_before - dist_after, 4)
        self.session_attempts.append({
            "issue_type": issue_type,
            "tactic": tactic,
            "dist_before": dist_before,
            "dist_after": dist_after,
            "progress": progress,
            "succeeded": progress > 0.005, # A minimal progress is required to be a success
        })

    def get_failed_tactics(self, issue_type: str) -> list[str]:
        """Gets tactics that have failed for a specific issue type in the current session."""
        return [
            a["tactic"] for a in self.session_attempts if a["issue_type"] == issue_type and not a["succeeded"]
        ]

    def update_history(self, data):
        self.historical_base.append(data)
    
    def update_analysis_history(self, data):
        self.historical_analyses.append(data)

    def get_last_monitor_output(self):
        if self.historical_base:
            return self.historical_base[-1]
        else:
            return None

    def get_last_analysis_output(self):
        """
        Retorna a última análise realizada pelo Analyzer.
        """
        if self.historical_analyses:
            return self.historical_analyses[-1]
        else:
            return None

    def query(self, issue_type: str) -> dict:
        return {
            "goal_threshold": self.data["goal_threshold"],
            "allowed_tasks": self.data["allowed_tasks"],
            "available_scripts": self.data["available_scripts"],
            "policy": self.data["policies"].get(issue_type, {}),
            "history": [
                h for h in self.data["adaptation_history"]
                if h["issue_type"] == issue_type
            ],
            "failed_tactics_this_session": self.get_failed_tactics(issue_type),
        }

knowledge_base = KnowledgeBase()
        