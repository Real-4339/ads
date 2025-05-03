import numpy as np
import pandas as pd
from loguru import logger

from ads.detect_algs.dwt_mlead.algorithm import main as dwt_mlead_detection
from ads.detect_algs.triple_es.algorithm import triple_es_predict


def calculate_jaccard_index(set1: set[int], set2: set[int]) -> float:
    """
    Calculates the Jaccard index (similarity measure) between two sets of indices.
    Returns a value from 0.0 (no overlap) to 1.0 (complete overlap)
    """
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    if union == 0:
        # If both sets are empty, they are identical
        return 1.0
    else:
        return intersection / union


def get_offset(data: np.ndarray) -> str:
    """
    Get the offset of the data
    """
    data = np.unique(data)
    differences = np.diff(data)
    median_diff = np.median(differences)

    if median_diff < 60:
        return str(int(median_diff)) + "S"
    elif median_diff < 3600:
        return str(int(median_diff / 60)) + "T"
    else:
        return str(int(median_diff / 3600)) + "H"


def to_series(data: np.ndarray, time: str) -> pd.Series:
    return pd.Series(range(len(data)), index=data).resample(time).count()


def map_resampled_indices_to_original(
    detected_resampled_indices: list[int],
    original_timestamps: np.ndarray,
    resampled_series: pd.Series,
) -> set[int]:
    """
    Maps indices from a resampled series (`resampled_series`) back
    to the indices of the original timestamp array (`original_timestamps`).
    """
    original_mapped_indices: set[int] = set()
    if (
        not detected_resampled_indices
        or len(original_timestamps) == 0
        or resampled_series is None
        or resampled_series.empty
    ):
        return original_mapped_indices
    if not isinstance(resampled_series.index, pd.DatetimeIndex):
        print(
            "Error: map_resampled_indices_to_original requires resampled_series with DatetimeIndex."
        )
        return original_mapped_indices

    try:
        original_datetimes = pd.to_datetime(original_timestamps, unit="s")
    except (ValueError, TypeError) as e:
        print(f"Error converting original_timestamps to datetime: {e}")
        return original_mapped_indices

    resampled_index = resampled_series.index

    for resampled_idx in detected_resampled_indices:
        if not (0 <= resampled_idx < len(resampled_index)):
            continue  # Skip invalid index

        bin_start = resampled_index[resampled_idx]
        bin_end = None
        if resampled_idx + 1 < len(resampled_index):
            bin_end = resampled_index[resampled_idx + 1]
        else:
            time_freq = pd.infer_freq(resampled_index)
            if time_freq:
                try:
                    bin_end = bin_start + pd.tseries.frequencies.to_offset(time_freq)
                except Exception:  # Error adding a frequency
                    pass

        if bin_end is not None:
            mask = (original_datetimes >= bin_start) & (original_datetimes < bin_end)
        else:  # If the end of the interval could not be determined
            mask = original_datetimes >= bin_start

        original_indices_in_bin = np.where(mask)[0]
        original_mapped_indices.update(original_indices_in_bin)

    return original_mapped_indices


def check_for_anomalies(name: str, data: np.ndarray) -> bool:
    """
    Check if the data contains anomalies.
    """
    # Placeholder for anomaly detection logic
    # For example, you can use z-score or IQR method to detect anomalies
    NO_ANOMALY = "N\\A"

    anomalies = {
        "regular": [],
        "random_daily": [],
        "trace": NO_ANOMALY,
        "interrupted": [14, 15],
        "sped_up": [21, 22],
        "slow_down": [31, 32],
    }

    print(f"\n-- Checking for anomalies in {name} --")

    results = {}

    print("Checking with epoch format: ")
    point_anom, cluster_anom = dwt_mlead_detection(data)

    if anomalies[name] == NO_ANOMALY:
        results["epoch"] = {
            "points_jaccard": 0,
            "clusters_jaccard": 0,
            "points": point_anom,
            "clusters": cluster_anom,
        }
    else:
        jaccard_points = calculate_jaccard_index(set(anomalies[name]), set(point_anom))
        jaccard_clusters = calculate_jaccard_index(
            set(anomalies[name]), set(cluster_anom)
        )
        results["epoch"] = {
            "points_jaccard": jaccard_points,
            "clusters_jaccard": jaccard_clusters,
        }

    print("Checking with time-diff format: ")
    new_data = np.diff(data)
    point_anom, cluster_anom = dwt_mlead_detection(new_data)

    point_set = set()
    cluster_set = set()

    for i in range(len(point_anom) - 1):
        if 0 <= point_anom[i] < len(data):
            point_set.add(point_anom[i])
        if 0 <= point_anom[i + 1] < len(data):
            point_set.add(point_anom[i + 1])

    for i in range(len(cluster_anom) - 1):
        if 0 <= cluster_anom[i] < len(data):
            cluster_set.add(cluster_anom[i])
        if 0 <= cluster_anom[i + 1] < len(data):
            cluster_set.add(cluster_anom[i + 1])

    if anomalies[name] == NO_ANOMALY:
        results["time-diff"] = {
            "points_jaccard": 0,
            "clusters_jaccard": 0,
            "points": point_set,
            "clusters": cluster_set,
        }
    else:
        jaccard_points = calculate_jaccard_index(set(anomalies[name]), point_set)
        jaccard_clusters = calculate_jaccard_index(set(anomalies[name]), cluster_set)
        results["time-diff"] = {
            "points_jaccard": jaccard_points,
            "clusters_jaccard": jaccard_clusters,
        }

    print("Checking with get_offset format: ")
    date_time = pd.to_datetime(data, unit="s")
    series = to_series(date_time, get_offset(data))
    point_anom, cluster_anom = dwt_mlead_detection(series.values)

    resampled_map = map_resampled_indices_to_original(point_anom, data, series)
    cluster_map = map_resampled_indices_to_original(cluster_anom, data, series)

    if anomalies[name] == NO_ANOMALY:
        results["get_offset"] = {
            "points_jaccard": 0,
            "clusters_jaccard": 0,
            "points": resampled_map,
            "clusters": cluster_map,
        }

    else:
        jaccard_points = calculate_jaccard_index(set(anomalies[name]), resampled_map)
        jaccard_clusters = calculate_jaccard_index(set(anomalies[name]), cluster_map)

        results["get_offset"] = {
            "points_jaccard": jaccard_points,
            "clusters_jaccard": jaccard_clusters,
        }

    for key, value in results.items():
        if value.get("points") is None:
            print(
                f"Method: {key}, Points Jaccard: {value['points_jaccard']}, Clusters Jaccard: {value['clusters_jaccard']}"
            )
        else:
            print(
                f"Method: {key}, Detected Points: {value['points']}, Detected Clusters: {value['clusters']}"
            )


def predict(data: np.ndarray):
    """
    Func that predicts the next values.
    """
    # offset = get_offset(data)

    if len(data) > 10:
        predictions = triple_es_predict(data)

    # logger.info(f"Predictions: \n{predictions}")

    return predictions
