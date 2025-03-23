import pandas as pd
from SimRH import run_simulation
from gamma_closed import compute_erf_expression


def main():
    # Choose the parameter to vary and define its values.
    # For example, to vary Vehicle_Lambda, use:
    varied_param = "Vehicle_Lambda"
    varied_values = [0.1, 0.125, 0.15, 0.175, 0.2, 0.225, 0.25, 0.2777]

    # Default simulation parameters
    default_parameters = {
        "mean_task_size": 3e9,
        "Cmin": 2e9,
        "Cmax": 4e9,
        "Vehicle_Lambda": 0.2,  # Default value; will be overridden if varied_param is Vehicle_Lambda
        "Task_Lambda": 10,
        "MAX_QUEUE_SIZE": 50,
    }

    N = 36  # Number of simulation runs per varied value

    # Prepare dictionary for aggregated (average) metrics
    aggregated_metrics = {
        varied_param: [],
        "GAMMA": [],  # New column computed once per row
        "VEHICLES": [],
        "PROCESSED": [],
        "PROCESSED AD": [],
        "FAILED": [],
        "AVG DELAY": [],
        "MISMATCH P": [],
        "AVG Q LENGTH": [],
        "BLOCKING P": [],
    }

    for val in varied_values:
        # Copy default parameters and update the parameter to vary
        sim_params = default_parameters.copy()
        sim_params[varied_param] = val

        # Initialize accumulators for each metric
        sum_metrics = {
            "VEHICLES": 0,
            "PROCESSED": 0,
            "PROCESSED AD": 0,
            "FAILED": 0,
            "AVG DELAY": 0,
            "MISMATCH P": 0,
            "AVG Q LENGTH": 0,
            "BLOCKING P": 0,
        }

        # Run simulation N times with the current parameter value
        for _ in range(N):
            result = run_simulation(
                mean_task_size=sim_params["mean_task_size"],
                Cmin=sim_params["Cmin"],
                Cmax=sim_params["Cmax"],
                Vehicle_Lambda=sim_params["Vehicle_Lambda"],
                Task_Lambda=sim_params["Task_Lambda"],
                MAX_QUEUE_SIZE=sim_params["MAX_QUEUE_SIZE"],
            )
            sum_metrics["VEHICLES"] += result["VEHICLES"]
            sum_metrics["PROCESSED"] += result["PROCESSED"]
            sum_metrics["PROCESSED AD"] += result["PROCESSED AD"]
            sum_metrics["FAILED"] += result["FAILED"]
            sum_metrics["AVG DELAY"] += result["AVG DELAY"]
            sum_metrics["MISMATCH P"] += result["MISMATCH P"]
            sum_metrics["AVG Q LENGTH"] += result["AVG Q LENGTH"]
            sum_metrics["BLOCKING P"] += result["BLOCKING P"]

        # Calculate the averages for the current value
        aggregated_metrics[varied_param].append(val)
        aggregated_metrics["VEHICLES"].append(sum_metrics["VEHICLES"] / N)
        aggregated_metrics["PROCESSED"].append(sum_metrics["PROCESSED"] / N)
        aggregated_metrics["PROCESSED AD"].append(sum_metrics["PROCESSED AD"] / N)
        aggregated_metrics["FAILED"].append(sum_metrics["FAILED"] / N)
        aggregated_metrics["AVG DELAY"].append(sum_metrics["AVG DELAY"] / N)
        aggregated_metrics["MISMATCH P"].append(sum_metrics["MISMATCH P"] / N)
        aggregated_metrics["AVG Q LENGTH"].append(sum_metrics["AVG Q LENGTH"] / N)
        aggregated_metrics["BLOCKING P"].append(sum_metrics["BLOCKING P"] / N)

        # Compute GAMMA once per row. Here, we compute it using Vehicle_Lambda.
        # If you're varying Vehicle_Lambda, this reflects the current value.
        gamma_value = compute_erf_expression(sim_params["Vehicle_Lambda"])
        aggregated_metrics["GAMMA"].append(gamma_value)

    # Create a DataFrame from the aggregated results
    df = pd.DataFrame(aggregated_metrics)

    print(f"\nAfter {N} runs per varied value of {varied_param}\n\n")
    print(df.to_string(index=False))

    # Export the DataFrame to CSV for further processing (e.g., MATLAB)
    df.to_csv("simulation_results.csv", index=False)


if __name__ == "__main__":
    main()
