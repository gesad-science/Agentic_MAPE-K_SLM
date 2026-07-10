import copy

class Executor:
    """
    A "real" executor that interprets the plan from the Planner and simulates
    the effect on the environment state. In a real-world scenario, this
    component would interface with the robot's control API.
    """
    def execute_plan(self, plan: dict, current_state: dict) -> dict:
        """
        Takes a plan and the current state, and returns the *new* state
        after the plan is "executed".
        """
        print("--- EXECUTING PLAN ---")
        next_state = copy.deepcopy(current_state)
        
        actions = plan.get('actions', [])
        print(f"Executing {len(actions)} actions from plan '{plan.get('selected_strategy')}'...")

        for action_item in actions:
            action_name = action_item.get('action')
            parameters = action_item.get('parameters', {})
            
            # Find the corresponding method in this class and call it
            # e.g., 'set_task' -> self.set_task(parameters, next_state)
            executor_method = getattr(self, action_name, self.unsupported_action)
            executor_method(parameters, next_state)
            
        # After all actions are executed, we can add some world physics simulation
        self.simulate_physics(next_state)

        return next_state

    def set_task(self, params: dict, state: dict):
        new_task = params.get('task')
        if new_task:
            print(f"  - Action: set_task to '{new_task}'")
            state['action']['task'] = new_task
        else:
            print("  - Action: set_task failed, no task parameter found.")

    def activate_script(self, params: dict, state: dict):
        script_name = params.get('script_name')
        if script_name:
            print(f"  - Action: activate_script '{script_name}'")
            state['action']['task'] = f"SCRIPTED_TASK.{script_name}"
            # Simulate the effect of the script
            if script_name == 'left_right':
                # This script is meant to clear obstacles
                state['obstacle']['presence'] = False
                print("    -> Effect: Obstacle presence set to False.")
        else:
            print("  - Action: activate_script failed, no script_name parameter found.")

    def advance_execution(self, params: dict, state: dict):
        mode = params.get('mode')
        print(f"  - Action: advance_execution with mode '{mode}'")
        current_task = state['action']['task']
        
        if current_task == 'PUSH' and mode == 'continue' and not state['obstacle']['presence']:
            current_dist = state['metrics']['dist_cube_target']
            state['metrics']['dist_cube_target'] = max(0, current_dist - 0.02) # Move 2cm closer
            print(f"    -> Effect: Cube pushed. New distance: {state['metrics']['dist_cube_target']:.4f}")
        elif current_task == 'PICK_AND_PLACE' and mode == 'regrasp' and state['obstacle']['presence']:
            # Simulate lifting the cube over a small obstacle
            obstacle_height = state['obstacle']['size'][2]
            if obstacle_height < 0.15: # Can clear obstacles up to 15cm high
                state['obstacle']['presence'] = False
                print("    -> Effect: Regrasped and lifted cube over obstacle.")

    def unsupported_action(self, params: dict, state: dict, action_name: str = "Unknown"):
        print(f"  - Warning: Unsupported action '{action_name}' called with params: {params}")

    def simulate_physics(self, state: dict):
        """A simple physics simulation step after actions are performed."""
        if state['metrics']['dist_cube_target'] < 0.01:
            state['metrics']['dist_cube_target'] = 0.0
            state['metrics']['success'] = True
            print("  - Physics: Cube snapped to target.")


