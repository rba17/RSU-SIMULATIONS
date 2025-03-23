import numpy as np
from scipy.stats import norm, uniform, poisson, geom


def run_simulation(
    mean_task_size, Cmin, Cmax, Vehicle_Lambda, Task_Lambda, MAX_QUEUE_SIZE=50
):

    TOTAL_TASKS = 1000  # Total number of tasks to be generated dynamically
    RSU_COVERAGE_DISTANCE = 1000  # meters
    V_MIN = 10
    V_MAX = 50
    FLOW_MAP = {
        0.1: (45, 13.5),
        0.125: (43.54, 13.062),
        0.15: (41.95, 12.585),
        0.175: (40.21, 12.063),
        0.2: (38.23, 11.469),
        0.225: (35.89, 10.767),
        0.25: (32.9, 9.87),
        0.2777: (24.78, 7.434),
    }
    MU, SIGMA = FLOW_MAP.get(Vehicle_Lambda, (None, None))
    if MU is None:
        raise ValueError("Vehicle_Lambda value not found in FLOW_MAP")

    p = 1 / mean_task_size

    # Initialize random seed for reproducibility if desired
    np.random.seed(None)

    class Vehicle:
        def __init__(self, id, entry_time):
            self.id = id
            self.speed = np.clip(norm.rvs(loc=MU, scale=SIGMA), V_MIN, V_MAX)
            self.capacity = uniform.rvs(loc=Cmin, scale=Cmax - Cmin)
            self.entry_time = entry_time
            self.residence_time = RSU_COVERAGE_DISTANCE / self.speed
            self.task_assigned = False  # Track if a task has been assigned

        def can_process_task(self, task_size, current_time):
            effective_capacity = RSU_COVERAGE_DISTANCE * (self.capacity / self.speed)
            return not self.task_assigned and task_size <= effective_capacity

        def assign_task(self, task_size, current_time):
            if self.can_process_task(task_size, current_time):
                self.task_assigned = True  # Mark this vehicle as occupied
                return True
            return False

    def generate_tasks(current_time, generated_tasks_count):
        num_new_tasks = min(
            poisson.rvs(Task_Lambda), TOTAL_TASKS - generated_tasks_count
        )
        task_sizes = geom.rvs(p, size=num_new_tasks)
        # Each task is a tuple: (task_size, deadline, arrival_time)
        return [
            (size, current_time + np.random.randint(1, 100), current_time)
            for size in task_sizes
        ]

    def traffic_simulation(vehicles, all_vehicles, current_time):
        for _ in range(poisson.rvs(Vehicle_Lambda)):
            vehicle_id = len(all_vehicles) + 1
            new_vehicle = Vehicle(vehicle_id, current_time)
            vehicles.append(new_vehicle)
            all_vehicles.append(new_vehicle)

    def simulate():
        tasks = []
        waiting_tasks = []
        vehicles = []
        all_vehicles = []
        current_time = 0
        tasks_processed = 0
        tasks_blocked = 0  # Counter for blocked tasks
        tasks_processed_after_deadline = 0
        generated_tasks_count = 0
        total_delay = 0
        total_queue_length = 0  # To calculate average queue length

        while generated_tasks_count < TOTAL_TASKS:
            new_tasks = generate_tasks(current_time, generated_tasks_count)
            for task in new_tasks:
                if len(tasks) < MAX_QUEUE_SIZE:
                    tasks.append(task)
                else:
                    waiting_tasks.append(task)
                    tasks_blocked += 1  # Task goes to waiting list (blocked)
            generated_tasks_count += len(new_tasks)

            # Try to move tasks from waiting to active queue if there's space
            while waiting_tasks and len(tasks) < MAX_QUEUE_SIZE:
                tasks.append(waiting_tasks.pop(0))

            traffic_simulation(vehicles, all_vehicles, current_time)
            total_queue_length += len(tasks)

            # Remove vehicles whose residence time has expired
            vehicles = [
                v for v in vehicles if (current_time - v.entry_time) < v.residence_time
            ]

            # Process tasks
            while tasks:
                task = tasks[0]
                task_allocated = False
                for vehicle in vehicles:
                    if vehicle.assign_task(task[0], current_time):
                        tasks_processed += 1
                        total_delay += current_time - task[2]
                        if current_time >= task[1]:  # Task processed after its deadline
                            tasks_processed_after_deadline += 1
                        tasks.pop(0)  # Remove task once assigned
                        task_allocated = True
                        break
                if not task_allocated:
                    break  # If the task is not allocated, exit the loop

            current_time += 1

        tasks_failed = len(tasks) + len(
            waiting_tasks
        )  # Remaining tasks are considered failed

        average_delay = total_delay / tasks_processed if tasks_processed > 0 else 0
        average_queue_length = (
            total_queue_length / current_time if current_time > 0 else 0
        )
        deadline_mismatch_probability = (
            tasks_processed_after_deadline / tasks_processed
            if tasks_processed > 0
            else 0
        )
        blocking_probability = (
            tasks_blocked / generated_tasks_count if generated_tasks_count > 0 else 0
        )

        # Return a dictionary of results
        results = {
            "VEHICLES": len(all_vehicles),
            "PROCESSED": tasks_processed,
            "PROCESSED AD": tasks_processed_after_deadline,
            "FAILED": tasks_failed,
            "AVG DELAY": average_delay,
            "MISMATCH P": deadline_mismatch_probability,
            "AVG Q LENGTH": average_queue_length,
            "BLOCKING P": blocking_probability,
        }
        return results

    return simulate()
