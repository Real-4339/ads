import os
import numpy as np

from datetime import datetime
from celery import Celery
from redis import Redis

from logger.conf import init_logger, log_predictions, log_basic, send_to_endpoint

# Create a Celery instance
app = Celery("tasks")
app.conf.broker_url = os.getenv("CELERY_BROKER_URL")
app.conf.result_backend = os.getenv("CELERY_RESULT_BACKEND")

r = Redis(host="redis", port=6379, db=0)
init_logger()


class LogAnalyzer:
    def __init__(self, source_name):
        self.source_name = source_name
        self.redis_key = f"{source_name}_state"
        self.errors_key = f"{source_name}_errors"
        self.max_errors = 50  # Max number of errors to keep in Redis

    def get_prediction_range(self, prediction, last_timestamp):
        """
        Calculates the range based on prediction and error history.
        Added 1 to max_error to avoid missing logs when predictions are really close.
        """
        errors = r.lrange(self.errors_key, 0, -1)
        predicted_interval = abs(prediction - last_timestamp)

        if not errors or len(errors) < 7:
            # If there's not enough data, we use ±40% from predicted_interval
            return [predicted_interval * 0.60, predicted_interval * 1.4]

        errors = [float(e.decode()) for e in errors]
        min_error = np.percentile(errors, 25)  # 25-й for lower bound
        max_error = np.percentile(errors, 95)  # 95-й for upper bound
        return [predicted_interval - min_error, predicted_interval + max_error + 1]

    def process_new_logs(self, timestamps: list, prediction: float):
        """Processes a list of new logs and updates the state"""

        state = r.hgetall(self.redis_key)
        if not state:
            # First run
            last_timestamp = timestamps[-1]
            prediction_range = self.get_prediction_range(prediction, last_timestamp)

        else:
            last_timestamp = float(state[b"last_timestamp"].decode())
            last_prediction = float(state[b"last_prediction"].decode())
            # No new logs
            if last_timestamp == timestamps[-1]:
                log_basic(f"No new logs for {self.source_name}")
                return float("inf")

            first_new_timestamp = [ts for ts in timestamps if ts > last_timestamp][0]
            interval = first_new_timestamp - last_timestamp

            send_to_endpoint(
                f"Diff - {interval}",
                source=self.source_name,
                level="DEBUG",
            )

            # Update statistics
            prediction_range = self.get_prediction_range(
                last_prediction, last_timestamp
            )

            error = abs(first_new_timestamp - last_prediction)
            r.rpush(self.errors_key, error)
            r.ltrim(self.errors_key, -self.max_errors, -1)  # Limit

            send_to_endpoint(
                f"Error - {error}",
                source=self.source_name,
                level="DEBUG",
            )

            if interval < prediction_range[0]:
                # log_predictions(
                log_basic(
                    f"First log too early: {first_new_timestamp}, \n\t\t\tfor {self.source_name},"
                    f"expected >= {last_timestamp + prediction_range[0]}, \n\t\t\t"
                    f"predicted: {last_prediction}",
                    level="WARNING",
                )
                send_to_endpoint(
                    f"First log too early: {first_new_timestamp}, "
                    f"expected >= {last_timestamp + prediction_range[0]}, "
                    f"predicted: {last_prediction}",
                    source=self.source_name,
                    level="WARNING",
                )
            elif interval > prediction_range[1]:
                # "Late" logs are handled by check_timestamp if no updates occur by timeout
                ...
            else:
                log_basic(
                    f"Got log/s with expected time range, got timestamp: {first_new_timestamp}, \n\t\t\t\t\t\t"
                    f"for {self.source_name}, "
                    f"predicted: {last_prediction}\n\t\t\t\t\t\t"
                    f"last_timestamp: {last_timestamp}",
                    level="SUCCESS",
                )
                send_to_endpoint(
                    f"Got log/s with expected time range, got timestamp: {first_new_timestamp}, "
                    f"predicted: {last_prediction}, "
                    f"last_timestamp: {last_timestamp}",
                    source=self.source_name,
                    level="SUCCESS",
                )

        # Save new state in Redis
        r.hset(
            self.redis_key,
            mapping={
                "last_timestamp": timestamps[-1],
                "last_prediction": prediction,
            },
        )

        return prediction_range[1]


@app.task
def check_timestamp(source_name: str, old_timestamp: float):
    """
    Checks if last_timestamp has been updated since the last check.
    Args:
        source_name (str): The name of the log source.
        expected_last_timestamp (float): The last timestamp at the time of startup.
    """
    state = r.hgetall(f"{source_name}_state")
    if not state:
        log_basic(f"Log {source_name}: No state found")

    current_last_timestamp = float(state[b"last_timestamp"].decode())

    if current_last_timestamp == old_timestamp:
        log_predictions(
            f"Log {source_name}: No update since {old_timestamp},\n\t\t\tmissing log detected",
            level="WARNING",
        )
        send_to_endpoint(
            f"Log {source_name}: No update since {old_timestamp}, missing log detected",
            source=source_name,
            level="WARNING",
        )


@app.task
def process_logs(source_name: str, timestamps: list, prediction: float):
    """
    Processes a list of new logs.
    Args:
        source_name (str): The name of the logs source.
        timestamps (list): The list of new timestamps.
        prediction (float): Predicted next timestamp.
        timeout_factor (float): Factor for timeout.
    """
    analyzer = LogAnalyzer(source_name)
    timeout = analyzer.process_new_logs(timestamps, prediction)

    if timeout == float("inf"):
        return

    log_basic(
        f"New Log {source_name}: "
        f"Timeout: {timeout + timestamps[-1]}, \n\t\t\t\t\t\tPrediction: {prediction}, "
        f"Last timestamp: {timestamps[-1]}"
    )
    send_to_endpoint(
        f"New Log {source_name}: "
        f"Timeout: {timeout + timestamps[-1]}, Prediction: {prediction}, "
        f"Last timestamp: {timestamps[-1]}",
        source=source_name,
        level="INFO",
    )

    # Start the monitoring task with eta = max_range
    max_range_ts = timeout + timestamps[-1]  # Convert max_range to timestamp
    check_timestamp.apply_async(
        (source_name, timestamps[-1]), eta=datetime.fromtimestamp(max_range_ts)
    )
