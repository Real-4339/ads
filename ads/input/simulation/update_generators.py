import numpy as np
import time
import random


def update_logs(logs: dict) -> dict:
    """
    Updates the logs with the next closest timestamps randomly
    """
    res = [
        len(logs["regular"]),
        len(logs["random_daily"]),
        len(logs["trace"]),
        len(logs["sped_up"]),
        len(logs["slow_down"]),
    ]
    while True:
        logs["regular"] = update_timestamps_regular(logs["regular"], 10)
        logs["random_daily"] = update_timestamps_random_daily(
            logs["random_daily"], 86400, 3600 * 2
        )
        logs["trace"] = update_timestamps_trace(logs["trace"])
        logs["sped_up"] = update_timestamps_regular(logs["sped_up"], 3)
        logs["slow_down"] = update_timestamps_regular(logs["slow_down"], 20)

        if res != [
            len(logs["regular"]),
            len(logs["random_daily"]),
            len(logs["trace"]),
            len(logs["sped_up"]),
            len(logs["slow_down"]),
        ]:
            break

    return logs


def update_timestamps_regular(
    timestamps: np.ndarray, frequency_seconds: int
) -> np.ndarray:
    """
    Updates the timestamps with a regular frequency
    """
    timestamp = timestamps[-1] + frequency_seconds
    while timestamp <= time.time():
        timestamps = np.append(timestamps, timestamp)
        timestamp += frequency_seconds

    return timestamps


def update_timestamps_random_daily(
    timestamps: np.ndarray, frequency_seconds: int, random_range_seconds: int
) -> np.ndarray:
    """
    Updates the timestamps with a random daily frequency
    """
    timestamp = timestamps[-1] + frequency_seconds
    while timestamp <= time.time():
        n_timestamp = timestamp + random.randint(
            -random_range_seconds // 2, random_range_seconds // 2
        )
        if n_timestamp > time.time():
            break
        timestamps = np.append(timestamps, n_timestamp)
        timestamp += frequency_seconds

    return timestamps


def update_timestamps_trace(timestamps: np.ndarray) -> np.ndarray:
    """
    Updates the timestamps with a trace frequency
    """
    timestamp = timestamps[-1]
    while True:
        repeat = random.choice([True, False])
        if not repeat:
            timestamp += 1
        if timestamp > time.time():
            break
        timestamps = np.append(timestamps, timestamp)
    return timestamps
