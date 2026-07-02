from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
from crewai import LLM, Agent, Task, Crew, Process
from crewai.project import CrewBase, task, crew, agent
import yaml, os
from tools import (
    get_last_monitor_output,
    get_last_analysis_output,
    get_current_target,
    is_cube_moving,
    is_cube_getting_closer_to_target
) 

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
                get_last_monitor_output,
                get_last_analysis_output,
                get_current_target,
                is_cube_moving,
                is_cube_getting_closer_to_target,

            ],
            llm=llm,
        )

    @task
    def analysi(self) -> Task:
        return Task(
            config=self.tasks_config["analysis"],
            agent=self.analyser_agent(),
        )

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
            agents=[self.analyser_agent()],  
            tasks=[
                self.analysi(),
                ],
            process=Process.sequential,
            verbose=True
        )