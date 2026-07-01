from monitor.models import Event

class EventDetector:
    def detect(self, row):
        events = []

        if row.target_changed:
            events.append(
                Event(
                    type="TARGET_CHANGED",
                    timestamp=row.timestep,
                    data={"new_target": row.active_target_name}
                )
            )
        
        if row.success:
            events.append(
                Event(
                    type="TASK_COMPLETED",
                    timestamp=row.timestep,
                    data={}
                )
            )
        
        if row.dist_ee_cube < 0.03:
            events.append(
                Event(
                    type="CUBE_REACHED",
                    timestamp=row.timestep,
                    data={}
                )
            )
        
        return events
