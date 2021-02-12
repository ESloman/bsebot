from mongo import interface


class BaseClass(object):
    """
    Base MongoDB DB Class. Provides basic method and properties that all other DB Classes will need.
    If not username or password is provided - authenticate without username and password.
    """
    def __init__(self, ip="192.168.0.15", username="admin", password="OrcsMordorSauron"):
        self.cli = interface.get_client(ip, username, password)
        self._vault = None

    @property
    def mongo_client(self):
        """
        Pymongo Client Object
        :return:
        """
        return self.cli

    @property
    def vault(self):
        return self._vault

    def insert(self, document):
        """
        Inserts the given object into this class' Collection object.
        :param document: document(s) to insert as dict or list of dicts
        :return:
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        if not isinstance(document, (list, dict)):
            raise IncorrectDocument("Given document isn't a dictionary or a list.")
        elif isinstance(document, list) and not all([isinstance(k, dict) for k in document]):
            raise IncorrectDocument("Not all documents in the list are dictionaries.")
        rets = interface.insert(self._vault, document)
        return rets

    def update(self, parameters, updated_vals):
        """
        Updates all documents based on the given parameters with the provided values.
        :param parameters:
        :param updated_vals:
        :return:
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        rets = interface.update(self.vault, parameters, updated_vals)
        return rets

    def delete(self, parameters, many=True):
        """
        Deletes documents based on the given parameters. If many=False, only deletes one else it deletes all matches.
        :param many: whether to delete all matching documents or just one
        :param parameters: Paramaters to match and delete on. Must be a dictionary.
        :return: number of deleted
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        rets = interface.delete(self.vault, parameters, many)
        return rets

    def query(self, parameters, limit=1000, projection=None, as_gen=False):
        """
        Searches a collection for documents based on given parameters.
        Parameters should be dictionaries : {key : search}. Where key is an existing key in the collection and
        search is either a value or an expression.
        Expressions can either be {operator: value} or {"$regex": regex_expression}. Regex can only be used on string fields.
        Valid operators: https://docs.mongodb.com/manual/reference/operator/query-comparison/
        Parameter examples:
            parameters = {"test_name": "tst_englishUK"}
            parameters = {"test_name": {"$gt": "tst_S"}}
            parameters = {"test_name": {"$regex": "tst_g.*"}}
        Projection examples:
            projection = {"_id": False}
        Args:
            parameters : dictionary as above
            limit : max number of results to return
            projection : dict of keys to return for each result
            as_gen : True returns generator (mongoDB cursor obj) and false returns list of results
        Returns a generator (cursor obj) if as_gen else returns a list of results
        """
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        return interface.query(self.vault, parameters, limit, projection, as_gen)

    def get_collection_names(self):
        if not hasattr(self, "database"):
            raise NoVaultError("No vault instantiated.")
        return interface.get_collection_names(self.database)

    def create_index(self, field):
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        return interface.create_index(self.vault, field)

    def get_indexes(self):
        if not self.vault:
            raise NoVaultError("No vault instantiated.")
        return interface.get_indexes(self.vault)


class NoVaultError(Exception):
    def __init__(self, message):
        super(NoVaultError, self).__init__(message)


class IncorrectDocument(Exception):
    def __init__(self, message):
        super(IncorrectDocument, self).__init__(message)
