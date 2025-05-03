import numpy as np
import pandas as pd

from dataclasses import dataclass
from .dwt_mlead import DWT_MLEAD


@dataclass
class CustomParameters:
    start_level: int = 3
    quantile_epsilon: float = 0.01
    random_state: int = 42


def main(data: np.ndarray, config: CustomParameters = CustomParameters()):
    np.random.seed(config.random_state)

    detector = DWT_MLEAD(
        data,
        start_level=config.start_level,
        quantile_boundary_type="percentile",
        quantile_epsilon=config.quantile_epsilon,
        track_coefs=True,  # just used for plotting
    )
    point_scores = detector.detect()
    point_anom: list = []
    cluster_anom: list = []

    try:
        print("\n=== Point anomalies ===")
        for i, score in enumerate(point_scores):
            if score > 0:
                point_anom.append(i)
                print(f"  Anomaly at {i} with score {score}")

        print("\n=== Cluster anomalies ===")
        clusters = detector.find_cluster_anomalies(
            point_scores, d_max=2.5, anomaly_counter_threshold=2
        )
        for c in clusters:
            if hasattr(c, "points") and c.points is not None:
                cluster_anom.extend(c.points)
            print(f"  Anomaly at {c.center} with score {c.score}")
    except Exception as e:
        print("No anomalies detected:", e)

    return point_anom, cluster_anom

    # save individual point scores instead of cluster centers
    # np.savetxt(config.dataOutput, point_scores, delimiter=",")
    # print("\n=== Storing results ===")
    # print(f"Saved **point scores** to {config.dataOutput}.")

    # detector.plot(coefs=False, point_anomaly_scores=point_scores)


if __name__ == "__main__":
    config = CustomParameters()
    main(config)
