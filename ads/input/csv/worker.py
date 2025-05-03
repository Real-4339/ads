import numpy as np
import time


def generate_timestamps(*arrays) -> list[np.ndarray]:
    """
    Recreate the timestamps from the input arrays.
    """
    # Current timestamp in epoch format (+ 3 minutes)
    current_time = time.time() + 180

    new_arrays = [shift_timestamps(array, current_time) for array in arrays]

    return new_arrays


def shift_timestamps(original_array, target_end_time):

    # Calculate intervals between timestamps in the source array
    intervals = np.diff(original_array)

    # Create a new array starting from target_end_time and moving backwards
    new_array = np.zeros_like(original_array, dtype=float)
    new_array[-1] = target_end_time  # The last element is the target timestamp

    # Fill the array from the end using the original intervals
    for i in range(len(intervals) - 1, -1, -1):  # From len(intervals) - 2 to 0
        new_array[i] = new_array[i + 1] - intervals[i]

    return new_array
