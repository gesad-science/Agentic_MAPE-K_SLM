from monitor.detectors import EventDetector
from knowledgeBase import KnowledgeBase

class Monitor:
    def __init__(self):
        self.detector = EventDetector()
        self.knowledge_base = KnowledgeBase()

    def process(self, row):
        robot = {
            "position": [
                float(row.ee_x),
                float(row.ee_y),
                float(row.ee_z)
            ],
            "velocity": [
                float(row.ee_vx),
                float(row.ee_vy),
                float(row.ee_vz)
            ],
            "joints": [
                float(row.joint_1),
                float(row.joint_2),
                float(row.joint_3),
                float(row.joint_4),
                float(row.joint_5),
                float(row.joint_6),
                float(row.joint_7)
            ],
            "joint_velocities": [
                float(row.joint_vel_1),
                float(row.joint_vel_2),
                float(row.joint_vel_3),
                float(row.joint_vel_4),
                float(row.joint_vel_5),
                float(row.joint_vel_6),
                float(row.joint_vel_7)
            ]
        }

        cube = {
            "position": [
                float(row.cube_x),
                float(row.cube_y),
                float(row.cube_z)
            ],
            "orientation": [
                float(row.cube_roll),
                float(row.cube_pitch),
                float(row.cube_yaw)
            ],
            "velocity": [
                float(row.cube_vx),
                float(row.cube_vy),
                float(row.cube_vz)
            ]
        }

        target = {
            "name": row.active_target_name,
            "index": int(row.active_target_index),
            "position": [
                float(row.target_x),
                float(row.target_y),
                float(row.target_z)
            ]
        }

        states = {
            "robot": robot,
            "cube": cube,
            "target": target
        }

        metrics = {
            "reward": float(row.reward),
            "success": bool(row.success),
            "dist_ee_cube": float(row.dist_ee_cube),
            "dist_cube_target": float(row.dist_cube_target)
        }

        events = self.detector.detect(row)

        self.knowledge_base.historical_base.extend(states)
        self.knowledge_base.historical_base.append(metrics)

        return {
            "episode": int(row.episode),
            "step": int(row.step),
            "robot": robot,
            "cube": cube,
            "target": target,
            "metrics": metrics,
            "events": events
        }