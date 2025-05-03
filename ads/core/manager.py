import os
import signal

from celery import group
from celery import Celery
from loguru import logger

from ads.filter.config import Config
from ads.input.interface import InputManager
from ads.core.logger.logger import init_logger
from ads.detect_algs.detect_system import predict, check_for_anomalies


CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
app = Celery("tasks", broker=CELERY_BROKER_URL, backend=CELERY_BROKER_URL)


class CoreManager:
    def __init__(self, input_manager: InputManager):
        """
        This class is used for managing the Core.
        """
        init_logger()
        self.__config = Config()
        self.__input_manager = input_manager

        # Signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame) -> None:
        """
        Handles the shutdown of the Core.
        """
        logger.info("Shutting down Core...")
        exit(0)

    def _get_logs(self) -> None:
        self.__input_manager.fetch_logs(self.__config.filters)

    def _core_func(self):

        tasks = []
        for name, value in self.__input_manager.logs.items():
            if len(value) < 15:
                continue
            prediction = predict(value)
            tasks.append(
                app.signature(
                    "tasks.process_logs", args=[name, value.tolist(), prediction]
                )
            )

        if tasks:
            job = group(tasks)
            group_result = job.apply_async()
            group_result.join()
            logger.info("All tasks completed")

    def _core_loop(self) -> None:
        """
        Starts the core loop.
        """
        logger.info("Starting Core Loop")
        self._get_logs()
        while True:
            self._core_func()
            self.__input_manager.update()

    def run(self) -> None:
        """Main function"""
        self._core_loop()

    def test_1(self):
        self._get_logs()
        self._core_func()
        while not self.__input_manager.update():
            ...
        for _ in range(350):
            self._core_func()
            self.__input_manager.update()

        logger.info("Test 1 finished")

    def test_2(self):
        self._get_logs()
        self._core_func()
        res = self.__input_manager.update(True)
        while res:
            self._core_func()
            res = self.__input_manager.update()
        logger.info("Test 2 finished")
