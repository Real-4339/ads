import time
import random

from pathlib import Path


def generate_csv(range: int = 50):
    end_timestamp = time.time() + 30
    irange = range

    # Create the header row
    current_file_path = Path(__file__).resolve().parent / "files"

    # Generate timestamps using each function
    timestamps1 = generate_timestamps_regular(end_timestamp, irange, 10)
    timestamps2 = generate_timestamps_random_daily(
        end_timestamp, irange, 86400, 3600 * 2
    )  # Random time within 2 hours
    timestamps3 = generate_timestamps_trace(end_timestamp, irange)
    timestamps4 = generate_timestamps_interrupted(end_timestamp, irange, 10, 15, 5)
    timestamps5 = generate_timestamps_speed_up(end_timestamp, irange, 15, 3, 20)
    timestamps6 = generate_timestamps_slow_down(end_timestamp, irange, 1, 20, 30)

    # Write timestamps to CSV files
    write_timestamps_to_csv(timestamps1, f"{current_file_path}/regular.csv")
    write_timestamps_to_csv(timestamps2, f"{current_file_path}/random_daily.csv")
    write_timestamps_to_csv(timestamps3, f"{current_file_path}/trace.csv")
    write_timestamps_to_csv(timestamps4, f"{current_file_path}/interrupted.csv")
    write_timestamps_to_csv(timestamps5, f"{current_file_path}/sped_up.csv")
    write_timestamps_to_csv(timestamps6, f"{current_file_path}/slow_down.csv")


def write_timestamps_to_csv(timestamps, filename):
    """
    Writes timestamps to a CSV file.

    Args:
        timestamps: A string containing timestamps separated by newlines.
        filename: The name of the CSV file.
    """
    timestamps = "timestamp\n" + timestamps

    with open(filename, "w") as csvfile:
        csvfile.write(timestamps)


def generate_timestamps_regular(end_timestamp, irange, frequency_seconds):
    """
    Generates timestamps with a regular frequency,
    ending as close to time.time() as possible.

    Args:
        end_timestamp: The ending timestamp.
        irange: The number of timestamps to generate.
        frequency_seconds: The frequency of the timestamps in seconds.

    Returns:
        A string containing timestamps separated by newlines.
    """
    csv_output = ""
    # Calculate the adjusted start timestamp to align with the end timestamp
    start_timestamp = end_timestamp - (irange - 1) * frequency_seconds
    for i in range(irange):
        csv_output += str(start_timestamp + i * frequency_seconds) + "\n"
    return csv_output


def generate_timestamps_random_daily(
    end_timestamp, irange, frequency_seconds, random_range_seconds
):
    """
    Generates timestamps with a daily frequency,
    but with a random offset within a given range.


    Args:
        end_timestamp: The ending timestamp.
        irange: The number of timestamps to generate.
        frequency_seconds: The frequency of the timestamps in seconds (e.g., 24 hours = 86400 seconds).
        random_range_seconds: The range of random offset in seconds (e.g., 2 hours = 7200 seconds).

    Returns:
        A string containing timestamps separated by newlines.
    """
    timestamps = str(end_timestamp) + "\n"
    current_timestamp = end_timestamp - frequency_seconds
    for i in range(irange - 1):
        random_offset = random.randint(
            -random_range_seconds // 2, random_range_seconds // 2
        )
        timestamp = current_timestamp + random_offset
        timestamps = str(timestamp) + "\n" + timestamps
        current_timestamp -= frequency_seconds
    return timestamps


def generate_timestamps_trace(end_timestamp, irange):
    """
    Generates timestamps with a very small, random frequency, simulating a trace.

    Args:
        end_timestamp: The ending timestamp.
        irange: The number of timestamps to generate.

    Returns:
        A string containing timestamps separated by newlines.
    """

    csv_output = ""
    current_timestamp = end_timestamp
    for i in range(irange):
        # Randomly decide whether to repeat the previous timestamp
        repeat = random.choice([True, False])

        if repeat:
            csv_output = str(current_timestamp) + "\n" + csv_output
            continue

        current_timestamp -= 1
        csv_output = str(current_timestamp) + "\n" + csv_output
    return csv_output


def generate_timestamps_interrupted(
    end_timestamp,
    irange,
    frequency_seconds,
    interruption_start,
    interruption_duration,
):
    """
    Generates timestamps with a regular frequency, but with an interruption in the middle*.

    Args:
        end_timestamp: The ending timestamp.
        irange: The number of timestamps to generate.
        frequency_seconds: The frequency of the timestamps in seconds.
        interruption_start: The index of the timestamp where the interruption starts.
        interruption_duration: The duration of the interruption in terms of number of timestamps.

    Returns:
        A string containing timestamps separated by newlines.
    """
    csv_output = ""
    start_timestamp = (
        end_timestamp - (irange - 1 + interruption_duration) * frequency_seconds
    )
    for i in range(irange):
        if interruption_start <= i < interruption_start + interruption_duration:
            start_timestamp += (
                frequency_seconds  # Make difference between timestamps bigger
            )
            continue
        csv_output += str(start_timestamp + i * frequency_seconds) + "\n"
    return csv_output


def generate_timestamps_speed_up(
    end_timestamp,
    irange,
    normal_frequency_seconds,
    speed_up_frequency_seconds,
    speed_up_start,
):
    """
    Generates timestamps that speed up at a certain point.

    Args:
        end_timestamp: The ending timestamp.
        irange: The number of timestamps to generate.
        normal_frequency_seconds: The normal frequency of the timestamps in seconds.
        speed_up_frequency_seconds: The faster frequency of the timestamps in seconds.
        speed_up_start: The index of the timestamp where the speed up starts.

    Returns:
        A string containing timestamps separated by newlines.
    """
    csv_output = str(end_timestamp) + "\n"
    current_timestamp = end_timestamp
    for i in range(irange - 1, -1, -1):
        if i >= speed_up_start:
            current_timestamp -= speed_up_frequency_seconds
            csv_output = str(current_timestamp) + "\n" + csv_output
        else:
            current_timestamp -= normal_frequency_seconds
            csv_output = str(current_timestamp) + "\n" + csv_output
    return csv_output


def generate_timestamps_slow_down(
    end_timestamp,
    irange,
    normal_frequency_seconds,
    slow_down_frequency_seconds,
    slow_down_start,
):
    """
    Generates timestamps that slow down at a certain point.

    Args:
        end_timestamp: The ending timestamp.
        irange: The number of timestamps to generate.
        normal_frequency_seconds: The normal frequency of the timestamps in seconds.
        slow_down_frequency_seconds: The slower frequency of the timestamps in seconds.
        slow_down_start: The index of the timestamp where the slow down starts.

    Returns:
        A string containing timestamps separated by newlines.
    """
    csv_output = str(end_timestamp) + "\n"
    current = end_timestamp
    for i in range(irange - 1, -1, -1):
        if i >= slow_down_start:
            current -= slow_down_frequency_seconds
            csv_output = str(current) + "\n" + csv_output
        else:
            current -= normal_frequency_seconds
            csv_output = str(current) + "\n" + csv_output

    return csv_output
