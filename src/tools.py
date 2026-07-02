from crewai.tools import tool
from crewai.tools import BaseTool
import math
from knowledgeBase import knowledge_base

knowledge_base = knowledge_base

@tool("Get Last Monitor Output")
def get_last_monitor_output() -> dict | None:
    """
    Retorna o último output produzido pelo agente Monitor.
    """
    return knowledge_base.get_last_monitor_output()

@tool("Get Last Analysis Output")
def get_last_analysis_output() -> dict | None:
    """
    Retorna a última análise produzida pelo agente Analyzer.
    """
    return knowledge_base.get_last_analysis_output()

@tool("Get Current Target")
def get_current_target(
    target: dict
) -> str:
    """
    Retorna o nome do target atualmente ativo.
    """

    return target["name"]

@tool("Is Cube Moving")
def is_cube_moving(
    cube_velocity: list[float],
    threshold: float = 1e-3
) -> bool:
    """
    Verifica se o cubo está em movimento com base em sua velocidade linear.

    Args:
        cube_velocity: Velocidade linear do cubo [vx, vy, vz].
        threshold: Velocidade mínima para considerar que há movimento.

    Returns:
        True se o cubo estiver se movendo, False caso contrário.
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
    Verifica a tendência da distância entre o cubo e o target.

    Returns:
        "closer"  -> distância diminuiu.
        "farther" -> distância aumentou.
        "stable"  -> distância permaneceu praticamente igual
                     ou não existe uma medição anterior.
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