from crewai.tools import tool
from crewai.tools import BaseTool
import math
import json
from typing import Type
from pydantic import BaseModel, Field
from knowledgeBase import knowledge_base

knowledge_base = knowledge_base

@tool("Get Last Monitor Output")
def get_last_monitor_output() -> dict | None:
    """
    Returns the last output produced by the Monitor agent.
    """
    return knowledge_base.get_last_monitor_output()

@tool("Get Last Analysis Output")
def get_last_analysis_output() -> dict | None:
    """
    Returns the last analysis produced by the Analyzer agent.
    """
    return knowledge_base.get_last_analysis_output()

@tool("Get Current Target")
def get_current_target(
    target: dict
) -> str:
    """
    Returns the name of the currently active target.
    """
    return target["name"]

@tool("Is Cube Moving")
def is_cube_moving(
    cube_velocity: list[float],
    threshold: float = 1e-3
) -> bool:
    """
    Checks if the cube is moving based on its linear velocity.

    Args:
        cube_velocity: Linear velocity of the cube [vx, vy, vz].
        threshold: Minimum speed to be considered as movement.

    Returns:
        True if the cube is moving, False otherwise.
    """

    speed = math.sqrt(
        cube_velocity[0]**2 +
        cube_velocity[1]**2 +
        cube_velocity[2]**2
    )

    return speed > threshold

@tool("Is Cube Getting Closer To Target")
def is_cube_getting_closer_to_target(
    current_distance: float,
    previous_distance: float | None = None,
    tolerance: float = 1e-4
) -> str:
    """
    Checks the distance trend between the cube and the target.

    Returns:
        "closer"  -> distance has decreased.
        "farther" -> distance has increased.
        "stable"  -> distance has remained almost the same or there is no previous measurement.
    """

    if previous_distance is None:
        return "stable"

    delta = previous_distance - current_distance

    if delta > tolerance:
        return "closer"

    if delta < -tolerance:
        return "farther"

    return "stable"

# @tool("Calculate Progress")
# def calculate_progress(dist_cube_target: float,
#                        initial_distance: float) -> float:
#     """
#     Calcula o percentual de progresso da tarefa.
#     """

#     if initial_distance == 0:
#         return 100.0

#     progress = (1 - dist_cube_target / initial_distance) * 100

#     return max(0.0, min(progress, 100.0))

# @tool("Calculate Cube Status")
# def calculate_cube_status(
#     monitor_output: dict,
#     threshold: float = 0.01
# ) -> str:
#     """
#     Recebe o JSON completo produzido pelo Monitor.
#     """
#     print("RECEBIDO:", monitor_output)

#     vx, vy, vz = monitor_output["cube"]["velocity"]

#     velocity = math.sqrt(vx**2 + vy**2 + vz**2)

#     if velocity < threshold:
#         return "STATIC"

#     return "MOVING"

# @tool("Calculate End Effector Status")
# def calculate_ee_status(current_distance: float,
#                         previous_distance: float,
#                         tolerance: float = 1e-4) -> str:
#     """
#     Determina o estado do End-Effector.
#     """

#     difference = current_distance - previous_distance

#     if abs(difference) < tolerance:
#         return "STOPPED"

#     if difference < 0:
#         return "APPROACHING"

#     return "MOVING_AWAY"

# @tool("Check Target Reached")
# def check_target_reached(success: bool) -> bool:
#     """
#     Verifica se a tarefa foi concluída.
#     """

#     return success

# @tool("Calculate Need Replan")
# def calculate_need_replan(
#     distances: list,
#     threshold: float = 0.01
# ) -> bool:
#     """
#     Verifica se houve estagnação nas últimas medições.
#     """

#     if len(distances) < 2:
#         return False

#     variation = max(distances) - min(distances)

#     return variation < threshold

# @tool("Calculate State")
# def calculate_state(
#     success: bool,
#     cube_status: str,
#     ee_status: str
# ) -> str:
#     """
#     Determina o estado geral da tarefa.
#     """

#     if success:
#         return "TASK_COMPLETED"

#     if ee_status == "APPROACHING":
#         return "MOVING_TO_CUBE"

#     if cube_status == "MOVING":
#         return "MOVING_TO_TARGET"

#     return "IDLE"


class QueryKnowledgeBaseInput(BaseModel):
    issue_type: str = Field(..., description="Detected issue type")


class QueryKnowledgeBaseTool(BaseTool):
    name: str = "query_knowledge_base"
    description: str = (
        "Queries the knowledge base to get policies, rules, available scripts, "
        "and adaptation history for the given issue_type."
    )
    args_schema: Type[BaseModel] = QueryKnowledgeBaseInput

    def _run(self, issue_type: str) -> str:
        return json.dumps(knowledge_base.query(issue_type), ensure_ascii=False)


class ListAvailableTacticsTool(BaseTool):
    name: str = "list_available_tactics"
    description: str = (
        "Lists all available high-level tactics the planner can use to form a plan."
    )

    def _run(self) -> str:
        # The source of truth for available tactics are the keys in the GeneratePlanTool's plan_map.
        # This ensures any listed tactic can be converted into a plan.
        plan_map_keys = [
            "continue_push",
            "switch_to_pick_and_place",
            "switch_to_reach",
            "activate_script_left_right",
            "hold_position",
        ]
        catalog = {
            "continue_push": "Continue the PUSH task towards the active target.",
            "switch_to_pick_and_place": "Switch to PICK_AND_PLACE.",
            "switch_to_reach": "Switch to REACH before manipulation.",
            "activate_script_left_right": "Use scripted side-to-side recovery behavior.",
            "hold_position": "Safely maintain the current state.",
        }
        tactics = [{"name": t, "description": catalog[t]} for t in plan_map_keys if t in catalog]
        return json.dumps(tactics, ensure_ascii=False)


class SimulateActionInput(BaseModel):
    tactic_name: str = Field(..., description="Exact name of the tactic")
    issue_type: str = Field(..., description="Detected issue type")
    current_task: str = Field(..., description="Current active task")
    dist_cube_target: float = Field(..., description="Distance from the cube to the target")


class SimulateActionTool(BaseTool):
    name: str = "simulate_action"
    description: str = (
        "Simulates a tactic and estimates its success score. "
        "The tactic_name field must be exactly one of the names returned by list_available_tactics."
    )
    args_schema: Type[BaseModel] = SimulateActionInput

    def _run(self, tactic_name: str, issue_type: str, current_task: str, dist_cube_target: float) -> str:
        kb_context = knowledge_base.query(issue_type)
        history = kb_context.get("history", [])

        base_map = {
            "continue_push": 0.70,
            "switch_to_pick_and_place": 0.76,
            "switch_to_reach": 0.45,
            "activate_script_left_right": 0.50,
            "hold_position": 0.20,
        }

        score = base_map.get(tactic_name, 0.30)
        for row in history:
            if row.get("strategy") == tactic_name:
                score = (score + row["success_rate"]) / 2

        if issue_type == "goal_not_reached_yet":
            if tactic_name == "continue_push" and current_task == "PUSH" and dist_cube_target <= 0.12:
                score += 0.08
            if tactic_name == "switch_to_reach":
                score -= 0.10

        if issue_type == "path_blocked":
            if tactic_name == "switch_to_pick_and_place":
                score += 0.08
            if tactic_name == "activate_script_left_right":
                score += 0.03

        score = max(0.0, min(score, 1.0))

        result = {
            "tactic": tactic_name,
            "predicted_success": round(score, 3),
        }
        return json.dumps(result, ensure_ascii=False)


class GeneratePlanInput(BaseModel):
    selected_tactic: str = Field(..., description="The name of the chosen tactic.")
    reasoning: str = Field(..., description="A brief explanation for why this tactic was chosen over the others, based on the simulation results.")


class GeneratePlanTool(BaseTool):
    name: str = "generate_plan"
    description: str = (
        "Generates the final executable plan from the chosen tactic and the reasoning behind the choice. "
        "This tool accepts the selected_tactic and a reasoning string."
    )
    args_schema: Type[BaseModel] = GeneratePlanInput

    def _run(self, selected_tactic: str, reasoning: str) -> str:
        plan_map = {
            "continue_push": {
                "selected_strategy": "continue_push",
                "actions": [
                    {"id": 1, "action": "set_task", "parameters": {"task": "PUSH"}},
                    {"id": 2, "action": "advance_execution", "parameters": {"mode": "continue"}},
                ],
                "expected_outcome": "reduce distance to target",
            },
            "switch_to_pick_and_place": {
                "selected_strategy": "switch_to_pick_and_place",
                "actions": [
                    {"id": 1, "action": "set_task", "parameters": {"task": "PICK_AND_PLACE"}},
                    {"id": 2, "action": "advance_execution", "parameters": {"mode": "regrasp"}},
                ],
                "expected_outcome": "improve manipulation success",
            },
            "switch_to_reach": {
                "selected_strategy": "switch_to_reach",
                "actions": [
                    {"id": 1, "action": "set_task", "parameters": {"task": "REACH"}},
                    {"id": 2, "action": "advance_execution", "parameters": {"mode": "approach"}},
                ],
                "expected_outcome": "refine object approach",
            },
            "activate_script_left_right": {
                "selected_strategy": "activate_script_left_right",
                "actions": [
                    {"id": 1, "action": "activate_script", "parameters": {"script_name": "left_right"}},
                    {"id": 2, "action": "advance_execution", "parameters": {"mode": "scripted"}},
                ],
                "expected_outcome": "avoid blockage and recover progress",
            },
            "hold_position": {
                "selected_strategy": "hold_position",
                "actions": [
                    {"id": 1, "action": "set_task", "parameters": {"task": "HOLD"}},
                ],
                "expected_outcome": "preserve safe terminal state",
            },
        }
        plan = plan_map.get(selected_tactic)
        if plan:
            plan["reasoning"] = reasoning
        return json.dumps(plan or {}, ensure_ascii=False)