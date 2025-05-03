from abc import ABC, abstractmethod


class InputManager(ABC):
    """Abstract base class for input managers."""

    def __init__(self):
        self.__logs: dict[str, list[int]]

    @property
    def logs(self) -> dict[str, list[int]]:
        return self.__logs

    @logs.setter
    def logs(self, logs: dict[str, list[int]]) -> None:
        self.__logs = logs

    @abstractmethod
    def fetch_logs(self, **kwargs):
        """Retrieve logs from the data source.

        Args:
            **kwargs: Keyword arguments specific to the data source.
        Saves the logs in the `self.__logs` attribute.
        """
        pass

    @abstractmethod
    def update(self, **kwargs):
        """Update the logs with new data.

        Args:
            **kwargs: Keyword arguments specific to the data source.
        Updates the `self.__logs` attribute with new data.
        """
        pass
