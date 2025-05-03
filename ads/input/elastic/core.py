import os
from pathlib import Path
from loguru import logger

from getpass import getpass
from dotenv import load_dotenv
from .conn import ElasticConnection
from .exceptions import (
    ElasticCoreIsNotActive,
    ElasticConnectionIsNotEstablished,
    ElasticConnectionIsAlreadyEstablished,
)

USER = os.getenv("USERNAME", "name")
PASS = os.getenv("USERPASS", "password")


class ElasticCore:
    """
    ElasticCore is the main class for the ElasticSearch connection.
    It is a singleton class, so it can be instantiated only once.
    """

    global USER, PASS
    __instance = None

    @staticmethod
    def get_instance() -> "ElasticCore":
        """
        Static access method.
        Constructs a new ElasticCore if it is not created yet.
        """
        if ElasticCore.__instance is None:
            ElasticCore()
        return ElasticCore.__instance

    def __init__(self):
        """
        Virtually private constructor.
        :raises Exception: if the class is instantiated more than once.
        :param active: if True, the ElasticConnection is established.
        """
        if ElasticCore.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            ElasticCore.__instance = self

        self.__active: bool = False

        self.__elastic_connection = None
        self._new_connection()

    @property
    def active(self) -> bool:
        """
        Returns the status of the ElasticCore.
        """
        return self.__active

    def _new_connection(self) -> None:
        """
        Creates a new ElasticSearch connection. Returns nothing.
        @setter for ElasticConnection.
        """
        if self.active:
            raise ElasticConnectionIsAlreadyEstablished()

        def get_credentials_from_user() -> tuple:
            username = input("Username: ")
            password = getpass("Password: ")

            return username, password

        try:
            username, password = get_credentials_from_user()
        except Exception as e:
            username, password = USER, PASS

        self.__elastic_connection = ElasticConnection(username, password)
        logger.success("ElasticConnection is established.")
        self.__active = True

    def _close_connection(self) -> None:
        """
        Closes the ElasticSearch connection.
        """
        if self.active is False:
            raise ElasticConnectionIsNotEstablished()
        self.__elastic_connection.close()
        logger.info("ElasticConnection is closed.")
        self.__active = False

    def get_connection(self) -> ElasticConnection:
        """
        @getter for ElasticConnection.
        """
        if self.active is False:
            raise ElasticCoreIsNotActive()
        return self.__elastic_connection.get_es()

    def test_connection(self) -> None:
        """
        Tests the ElasticSearch connection.
        """
        if self.__elastic_connection is None:
            raise ElasticCoreIsNotActive()
        self.__elastic_connection.test()
