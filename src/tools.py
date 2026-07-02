from crewai.tools import tool
from crewai.tools import BaseTool
import math
from knowledgeBase import KnowledgeBase

knowledge_base = KnowledgeBase()

@tool("Consultar histórico a análises")
def get_history_analyses(args=None):
    """Retorna até as 10 últimas análises realizadas."""
    return knowledge_base.get_history()[-2:]

@tool("Calculate Progress")
def calculate_progress(dist_cube_target: float,
                       initial_distance: float) -> float:
    """
    Calcula o percentual de progresso da tarefa.
    """

    if initial_distance == 0:
        return 100.0

    progress = (1 - dist_cube_target / initial_distance) * 100

    return max(0.0, min(progress, 100.0))

@tool("Calculate Cube Status")
def calculate_cube_status(
    monitor_output: dict,
    threshold: float = 0.01
) -> str:
    """
    Recebe o JSON completo produzido pelo Monitor.
    """
    print("RECEBIDO:", monitor_output)

    vx, vy, vz = monitor_output["cube"]["velocity"]

    velocity = math.sqrt(vx**2 + vy**2 + vz**2)

    if velocity < threshold:
        return "STATIC"

    return "MOVING"

@tool("Calculate End Effector Status")
def calculate_ee_status(current_distance: float,
                        previous_distance: float,
                        tolerance: float = 1e-4) -> str:
    """
    Determina o estado do End-Effector.
    """

    difference = current_distance - previous_distance

    if abs(difference) < tolerance:
        return "STOPPED"

    if difference < 0:
        return "APPROACHING"

    return "MOVING_AWAY"

@tool("Check Target Reached")
def check_target_reached(success: bool) -> bool:
    """
    Verifica se a tarefa foi concluída.
    """

    return success

@tool("Calculate Need Replan")
def calculate_need_replan(
    distances: list,
    threshold: float = 0.01
) -> bool:
    """
    Verifica se houve estagnação nas últimas medições.
    """

    if len(distances) < 2:
        return False

    variation = max(distances) - min(distances)

    return variation < threshold

@tool("Calculate State")
def calculate_state(
    success: bool,
    cube_status: str,
    ee_status: str
) -> str:
    """
    Determina o estado geral da tarefa.
    """

    if success:
        return "TASK_COMPLETED"

    if ee_status == "APPROACHING":
        return "MOVING_TO_CUBE"

    if cube_status == "MOVING":
        return "MOVING_TO_TARGET"

    return "IDLE"