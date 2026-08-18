from core.config import settings
from pymilvus import MilvusClient, DataType

client = MilvusClient(uri=f"http://{settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
