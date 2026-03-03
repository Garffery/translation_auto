from pymilvus import MilvusClient, AnnSearchRequest, RRFRanker
from langchain_ollama import OllamaEmbeddings

class MilvusService:
    def __init__(self, uri:str, db_name:str, collection_name:str, embedding: OllamaEmbeddings):
        self.collection_name = collection_name
        self.embedding = embedding
        self.client = MilvusClient(uri=uri, db_name=db_name)


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
        query_token = self.embedding.embed_query(query_str)
        search_params_dense = {
            "metric_type": "COSINE",
            "params": {"nprobe": 2}
        }
        request_dense = AnnSearchRequest([query_token], "vector", search_params_dense, limit=2)

        search_params_bm25 = {
            "metric_type": "BM25"
        }

        # Create a BM25 text search request
        request_bm25 = AnnSearchRequest([query_str], "sparse", search_params_bm25, limit=2)

        # Combine the two requests
        reqs = [request_dense, request_bm25]

        # Initialize the RRF ranking algorithm
        ranker = RRFRanker(100)

        # Perform the hybrid search
        hybrid_search_res = self.client.hybrid_search(
            collection_name="collection_hy_1",
            reqs=reqs,
            ranker=ranker,
            limit=2,
            output_fields=["text", "source"]
        )

        pass