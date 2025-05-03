class ElasticCoreIsNotActive(Exception):
    def __init__(self):
        super().__init__("ElasticCore class is not created.")


class ElasticConnectionIsAlreadyEstablished(Exception):
    def __init__(self):
        super().__init__("ElasticConnection is already established.")


class ElasticConnectionIsNotEstablished(Exception):
    def __init__(self):
        super().__init__("ElasticConnection is not established.")