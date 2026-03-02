from pymilvus import MilvusClient


class MilvusService:
    def __init__(self, uri:str, db_name:str, collection_name:str):
        self.collection_name = collection_name
        self.client = MilvusClient(uri = uri, db_name = db_name)


    async def query(self, collection_name:str, query_str:str):
        """
        向量检索
        :param collection_name:
        :param query_str:
        :return:
        """
        pass


    async def hy_query(self, collection_name:str, query_str:str):
        """
        混合检索
        :param collection_name:
        :param query_str:
        :return:
        """

        pass