from knowledgeBase import KnowledgeBase
import math

class MetricsAnalyser:
    def __init__(self, knowledge):
        self.knowledge = knowledge

    def movement_metrics(self, monitor_output):
        last_data_monitor = self.knowledge.get_last_monitor_output()

        if last_data_monitor is None:
            return {
                "vertical_movement": False,
                "horizontal_movement_x": False,
                "horizontal_movement_y": False
            }

        current_pos = monitor_output["cube"]["position"]
        previous_pos = last_data_monitor["cube"]["position"]

        current_x, current_y, current_z = current_pos
        previous_x, previous_y, previous_z = previous_pos

        vertical_movement = current_z != previous_z
        horizontal_movement_x = current_x != previous_x
        horizontal_movement_y = current_y != previous_y

        movement = {
            "vertical_movement": vertical_movement,
            "horizontal_movement_x": horizontal_movement_x,
            "horizontal_movement_y": horizontal_movement_y
        }

        return movement
    
    def cube_status(self, vertical_movement, horizontal_movement_x, horizontal_movement_y):
        if vertical_movement or horizontal_movement_x or horizontal_movement_y:
            return "moving"
        else:
            return "stationary"
        
    def possible_obstacle(self, monitor_output, tolerance=1e-4, velocity_threshold=1e-3):
        """
        Detecta um possível bloqueio por obstáculo.

        Regra:
        - Existe obstáculo no ambiente;
        - O cubo não se move horizontalmente (X e Y);
        - O robô continua tentando se mover.
        """

        last_data_monitor = self.knowledge.get_last_monitor_output()

        # Não há histórico suficiente para comparação
        if last_data_monitor is None:
            return False

        # Existe obstáculo?
        obstacle_present = monitor_output["obstacle"]["presence"]

        # Posição atual e anterior do cubo
        current_x, current_y, _ = monitor_output["cube"]["position"]
        previous_x, previous_y, _ = last_data_monitor["cube"]["position"]

        # Movimento horizontal do cubo
        cube_moved_x = abs(current_x - previous_x) > tolerance
        cube_moved_y = abs(current_y - previous_y) > tolerance

        cube_not_moving_horizontal = not (cube_moved_x or cube_moved_y)

        # Velocidade do robô
        vx, vy, vz = monitor_output["robot"]["velocity"]
        robot_speed = math.sqrt(vx**2 + vy**2 + vz**2)

        robot_trying_to_move = robot_speed > velocity_threshold

        # Regra determinística
        obstacle_blocking = (
            obstacle_present
            and cube_not_moving_horizontal
            and robot_trying_to_move
        )

        return obstacle_blocking
    
    def execute(self, monitor_output):
        movement = self.movement_metrics(monitor_output)

        cube_status = self.cube_status(
            movement["vertical_movement"],
            movement["horizontal_movement_x"],
            movement["horizontal_movement_y"]
        )

        obstacle_blocking = self.possible_obstacle(monitor_output)

        analysis_result = {
            "movement": {
                "vertical_movement": movement["vertical_movement"],
                "horizontal_movement": {
                    "x": movement["horizontal_movement_x"],
                    "y": movement["horizontal_movement_y"]
                }
            },
            "cube": {
                "status": cube_status
            },
            "obstacle": {
                "blocking": obstacle_blocking
            }
        }

        return analysis_result 
    
            






# if __name__ == "__main__":
#     knowledge_base = KnowledgeBase()
#     knowledge_base.update_history({
#         "type": "monitor",
#         "data": {
#             "position": [0, 0],
#             "velocity": [1, 1],
#             "obstacle_detected": False
#         }
#     })
#     analyser = MetricsAnalyser(knowledge_base)

#     # Simulando a entrada do monitor_output
#     monitor_output = {
#         "type": "monitor",
#         "data": {
#             "position": [1, 2],
#             "velocity": [0.5, 0.5],
#             "obstacle_detected": True
#         }
#     }

#     analyser.moviment_metrics(monitor_output)