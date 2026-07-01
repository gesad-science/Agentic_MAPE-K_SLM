from monitor.detectors import EventDetector
from monitor.models import RobotState, CubeState, TargetState, Metrics, MonitorOutput

class Monitor:
    def __init__(self):
        self.detector = EventDetector()

    def process(self, row):
        robot = RobotState(
            position=(
                row.ee_x,
                row.ee_y,
                row.ee_z
            ),
            velocity=(
                row.ee_vx,
                row.ee_vy,
                row.ee_vz
            ),
            joints=[
                row.joint_1,
                row.joint_2,
                row.joint_3,
                row.joint_4,
                row.joint_5,
                row.joint_6,
                row.joint_7
            ],
            joint_velocities=[
                row.joint_vel_1,
                row.joint_vel_2,
                row.joint_vel_3,
                row.joint_vel_4,
                row.joint_vel_5,
                row.joint_vel_6,
                row.joint_vel_7
            ]
        )

        cube = CubeState(
            position=(
                row.cube_x,
                row.cube_y,
                row.cube_z
            ),

            orientation=(
                row.cube_roll,
                row.cube_pitch,
                row.cube_yaw
            ),

            velocity=(
                row.cube_vx,
                row.cube_vy,
                row.cube_vz
            )
        )

        target = TargetState(
            name=row.active_target_name,
            index=row.active_target_index,
            position=(
                row.target_x,
                row.target_y,
                row.target_z
            )
        )

        metrics = Metrics(
            reward=row.reward,
            success=row.success,
            dist_ee_cube=row.dist_ee_cube,
            dist_cube_target=row.dist_cube_target 
        )

        events = self.detector.detect(row)

        return MonitorOutput(
            episode=row.episode,
            step=row.step,
            robot=robot,
            cube=cube,
            target=target,
            metrics=metrics,
            events=events
        )