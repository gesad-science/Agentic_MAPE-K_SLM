from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai import LLM, Agent, Task, Crew, Process
from crewai.project import CrewBase, task, crew, agent
from tools import (
    QueryKnowledgeBaseTool,
    ListAvailableTacticsTool,
    SimulateActionTool,
    GeneratePlanTool
)


llm = LLM(model="ollama/qwen2.5:7b", temperature=0)

@CrewBase
class AnalyserCrew:

    agents_config = "config/analyser_agents.yaml"
    tasks_config = "config/analyser_tasks.yaml"

    @agent
    def analyser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['analyser_agent'],
            verbose=True,
            llm=llm,
        )

    @task
    def analysis(self) -> Task:
        return Task(config=self.tasks_config['analysis'])

    # @task
    # def analysis_diagnosis(self) -> Task:
    #     return Task(
    #         config=self.tasks_config["analysis_diagnosis"],
    #         agent=self.analyser_agent(),
    #         context=[
    #             self.metrics_analyser()
    #         ]
    #     )

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

@CrewBase
class PlannerCrew:
    """Planner crew for creating adaptation plans."""
    agents_config = 'config/planner_agents.yaml'
    tasks_config = 'config/planner_tasks.yaml'

    @agent
    def planner_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['planner_agent'],
            tools=[
                QueryKnowledgeBaseTool(),
                ListAvailableTacticsTool(),
                SimulateActionTool(),
                GeneratePlanTool()
            ],
            llm=llm,
            verbose=True,
            allow_delegation=False
        )

    @task
    def planning_task(self) -> Task:
        return Task(config=self.tasks_config['planning_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            verbose=True
        )