from dataclasses import dataclass
from typing import List

@dataclass
class RobotState:
    position: tuple
    velocity: tuple
    joints: List[float]
    joint_velocities: List[float]

@dataclass
class CubeState:
    position: tuple
    orientation: tuple
    velocity: tuple

@dataclass
class TargetState:
    name: str
    index: int
    position: tuple

@dataclass
class Event:
    type: str
    timestamp: float
    data: dict

@dataclass
class Metrics:
    reward: float
    success: bool
    dist_ee_cube: float
    dist_cube_target: float

@dataclass
class MonitorOutput:
    episode: int
    step: int
    robot: RobotState
    cube: CubeState
    target: TargetState
    metrics: Metrics
    events: list