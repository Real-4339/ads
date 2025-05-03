import pandas as pd

from datetime import datetime
from loguru import logger

from .core import ElasticCore
from .exceptions import ElasticCoreIsNotActive


class ElasticQueries:
    def __init__(self, elastic_core: ElasticCore):
        self.__elastic_core = elastic_core
        self.filters: dict

    def get_logs_from_interval(
        self,
        start_time: datetime,
        end_time: datetime,
    ) -> dict[str, list[float]]:
        """
        Returns all the logs from logs-* index.
        """

        if not self.__elastic_core.active:
            raise ElasticCoreIsNotActive

        query = {
            "size": 10000,
            "sort": [{"@timestamp": {"order": "desc"}}],  # Get last logs first
            "query": {
                "bool": {
                    "must": [
                        {"wildcard": {"_index": "logs-*"}},
                        {"range": {"@timestamp": {"gte": start_time, "lte": end_time}}},
                    ]
                }
            },
            "_source": ["@timestamp", "rfc5424.data.host", "host.hostname"],
        }

        return_data = {}

        while True:
            logger.info("Querying logs with query")
            search_res = self.__elastic_core.get_connection().search(
                index="logs-*", body=query
            )
            hits = search_res["hits"]["hits"]
            if not hits:
                break
            for hit in hits:
                log = hit["_source"]
                # Determine filter name based on host fields
                name = log.get("rfc5424", {}).get("data", {}).get("host")
                if name == "-" or name is None:
                    name = log.get("host", {}).get("hostname")
                try:
                    properties = self.filters.get(name, {}).property
                except Exception as e:
                    properties = []
                column_name = "->".join(
                    [name] + self._get_values_by_property_path(log, properties)
                )

                return_data.setdefault(column_name, []).append(log["@timestamp"])

                last_hit_time = hits[-1]["_source"]["@timestamp"]
                query["search_after"] = [last_hit_time]

        return return_data

    def _get_values_by_property_path(self, log: dict, property_path: list[str]) -> list:
        """
        Returns the values of the property path.

        :param property_path: The property path, e.g. ["rfc5424.data.host"]
        """
        result = []
        for prop in property_path:
            current = log
            try:
                for key in prop.split("."):
                    current = current[key]
                result.append(current)
            except (KeyError, TypeError):
                result.append("none")
        return result
