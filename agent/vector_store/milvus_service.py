import asyncio
from typing import List

from pymilvus import MilvusClient, AnnSearchRequest, RRFRanker
from langchain_ollama import OllamaEmbeddings

from config.setting import settings


class MilvusService:
    def __init__(self, uri:str, db_name:str, collection_name:str):
        self.collection_name = collection_name
        params = {"model": settings.OLLAMA_EMBEDDING_MODEL, "base_url": settings.OLLAMA_EMBEDDING_BASE_URL}
        self.embedding = OllamaEmbeddings(**params)
        self.client = MilvusClient(uri=uri, db_name=db_name)


    async def query(self, collection_name:str, query_str:str):
        """
        向量检索
        :param collection_name:
        :param query_str:
        :return:
        """
        pass


    async def hy_query(self, collection_name:str, query_str:str)-> List[dict]:
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

        return hybrid_search_res[0]

print(settings.MILVUS_DATABASE_NAME)
milvus_service = MilvusService(settings.MILVUS_CONNECTION_URL,
                               settings.MILVUS_DATABASE_NAME,
                               settings.MILVUS_COLLECTION_NAME)


if __name__ == '__main__':
    async def main():
        res = await milvus_service.hy_query(collection_name="collection_hy_1", query_str="血量")
        print(f"混合检索结果：{res}")


    asyncio.run(main())