import urllib3

from loguru import logger
from elasticsearch import Elasticsearch


class ElasticConnection:
    def __init__(self, username, password):
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        self.nodes = [
            "https://10.102.1.21:9200",
            "https://10.102.1.22:9200",
        ]

        self.es = Elasticsearch(
            self.nodes,
            http_auth=(username, password),
            verify_certs=False,
            timeout=60,
        )

    def get_es(self) -> Elasticsearch:
        """
        Returns the ElasticSearch connection.
        """
        return self.es

    def close(self) -> None:
        """
        Closes the connection.
        """
        self.es.close()

    def test(self) -> None:
        """
        Tests the connection.
        Prints logs from "logs-*" index.
        """
        try:
            query = {"query": {"match_all": {}}}
            search_results = self.es.search(index="logs-*", body=query)

            for hit in search_results["hits"]["hits"]:
                logger.trace(hit["_source"])

        except ConnectionError as e:
            logger.error(f"Conn prob: {e}")
        except Exception as e:
            logger.warning(f"Other: {e}")
