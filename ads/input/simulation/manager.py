import pandas as pd
from pathlib import Path

from ads.input.interface import InputManager
from .generate import generate_csv
from .update_generators import update_logs, time, np


class SimulationManager(InputManager):
    def __init__(self) -> None:
        """
        Initializes the SimulationManager class, and generates the csv files
        """
        super().__init__()
        generate_csv()

    def fetch_logs(self, filters: dict):
        """
        Returns all the logs from files folder
        """
        current_file_path = Path(__file__).resolve().parent / "files"
        filenames = [
            "regular.csv",
            "random_daily.csv",
            "trace.csv",
            "interrupted.csv",
            "sped_up.csv",
            "slow_down.csv",
        ]
        data_dict: dict[str, np.ndarray] = {}
        for filename in filenames:
            df = pd.read_csv(f"{current_file_path}/{filename}", usecols=["timestamp"])
            data_dict[filename[:-4]] = df["timestamp"].values

        self.logs = data_dict

    def update(self) -> bool:
        """
        Updates the logs
        """
        if self.logs["sped_up"][-1] > time.time():
            return False

        self.logs = update_logs(self.logs)

        return True
