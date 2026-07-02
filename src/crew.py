from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai import LLM, Agent, Task, Crew, Process
from crewai.project import CrewBase, task, crew, agent
import yaml, os
from tools import calculate_state, get_history_analyses, calculate_progress, calculate_cube_status, calculate_ee_status, check_target_reached,calculate_need_replan   

llm = LLM(model="ollama/qwen2.5:7b", temperature=0)

@CrewBase
class AnalyserCrew:

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    @agent
    def analyser_agent(self) -> Agent:
        print("AGENTS CONFIG KEYS:", self.agents_config.keys())

        return Agent(
            config=self.agents_config["analyse_agent"],
            verbose=True,
            tools=[
                get_history_analyses,
                calculate_progress,
                calculate_cube_status,
                calculate_ee_status,
                check_target_reached,
                calculate_state,
                calculate_need_replan
            ],
            llm=llm,
        )

    @task
    def query_knowledge_base(self) -> Task:
        return Task(
            config=self.tasks_config["query_knowledge_base"],
            agent=self.analyser_agent(),
        )

    @task
    def metrics_analyser(self) -> Task:
        return Task(
            config=self.tasks_config["metrics_analyser"],
            agent=self.analyser_agent(),
            context=[self.query_knowledge_base()],
        )

    @task
    def analysis_diagnosis(self) -> Task:
        return Task(
            config=self.tasks_config["analysis_diagnosis"],
            agent=self.analyser_agent(),
            context=[
                self.query_knowledge_base(),
                self.metrics_analyser()
            ]
        )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=[self.analyser_agent()],  
            tasks=[
                self.query_knowledge_base(),
                self.metrics_analyser(),
                self.analysis_diagnosis()
            ],
            process=Process.sequential,
            verbose=True
        )