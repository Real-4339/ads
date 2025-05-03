import numpy as np
from time import time, sleep

from ads.input.interface import InputManager
from .data_processor import DataProcessor
from .worker import generate_timestamps
from .data import Data


class CSVManager(InputManager):
    def __init__(self) -> None:
        """
        brute, secrepo, bgl
        """
        super().__init__()

        processor = DataProcessor("bgl", True)
        if not processor.exist:
            processor.save_to_files()

        processor = DataProcessor("secrepo_access")
        if not processor.exist:
            processor.save_to_files()

        processor = DataProcessor("brute_forse")
        if not processor.exist:
            processor.save_to_files()

        self.dt = Data()
        self.dt.load()
        self.current_indices = [0, 0, 0]

    def fetch_logs(self, filters: dict):
        """
        Returns all the logs from files folder
        """
        data_dict = {
            "brute_test": None,
            "secrepo_test": None,
            "bgl_test": None,
        }
        self.data = generate_timestamps(
            self.dt.get_epoch(self.dt.brute_test),
            self.dt.get_epoch(self.dt.secrepo_test),
            self.dt.get_epoch(self.dt.bgl_test),
        )

        current_time = time()

        # Find the nearest timestamps <= current_time and trim the arrays
        for ind, array in enumerate(self.data):
            # Find the index of the nearest timestamp <= current_time
            closest_idx = np.searchsorted(array, current_time, side="right") - 1
            if closest_idx < 0:  # If all timestamps are greater than current_time
                closest_idx = 0
            # Trim the array up to this index (inclusive)
            data_dict[list(data_dict.keys())[ind]] = array[: closest_idx + 1]
            # Set initial indexes
            self.current_indices[ind] = closest_idx + 1

        self.logs = data_dict

    def update(self, first: bool = False) -> bool:
        """
        Updates self.logs with the next closest timestamps randomly and returns True if more data exists.
        """
        if first:
            sleep(60 * 2)  # Имитация задержки

        if self.logs is None:
            return False  # Если fetch_logs еще не вызван

        data_dict = self.logs.copy()  # Копируем текущие логи
        current_time = time()
        has_more_data = False  # Флаг, есть ли еще данные

        # Проходим по каждому массиву
        for ind, key in enumerate(data_dict.keys()):
            array = self.data[ind]
            # Проверяем, есть ли еще данные в массиве
            if self.current_indices[ind] < len(array):
                has_more_data = True
                # Находим следующий ближайший timestamp <= current_time
                closest_idx = np.searchsorted(array, current_time, side="right") - 1
                if closest_idx < 0:
                    closest_idx = 0
                # Если новый индекс больше текущего, обновляем
                if closest_idx >= self.current_indices[ind]:
                    data_dict[key] = array[: closest_idx + 1]
                    self.current_indices[ind] = closest_idx + 1

        self.logs = data_dict
        return has_more_data
