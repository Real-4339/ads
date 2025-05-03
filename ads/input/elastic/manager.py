from datetime import datetime, timedelta

from .core import ElasticCore
from .queries import ElasticQueries
from ads.input.interface import InputManager


class ElasticManager(InputManager):
    def __init__(self) -> None:
        """
        This class is used for managing the ElasticSearch.
        :start: datetime
        :end: datetime
        """
        super().__init__()
        self.start = (datetime.now() - timedelta(minutes=10)).isoformat()
        self.end = datetime.now().isoformat()

        self.__elastic_core = ElasticCore.get_instance()
        self.__elastic_queries = ElasticQueries(self.__elastic_core)

    def fetch_logs(self, filters: dict):
        """
        Returns all the logs from logs-* index.
        """
        self.__elastic_queries.filters = filters
        self.__logs = self.__elastic_queries.get_logs_from_interval(
            self.start, self.end
        )
