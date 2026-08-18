from core.config import settings
from dbase.milvus.connection import client
from dbase.milvus.schema import schema as scm

index_params = client.prepare_index_params()
index_params.add_index(
    field_name="vector", index_type="IVF_FLAT", metric_type="L2", params={"nlist": 128}
)


def create_collection():
    client.create_collection(
        collection_name=settings.MILVUS_FIRST_COLLECTION,
        schema=scm,
        index_params=index_params,
    )


def create_index():
    client.create_index(
        collection_name=settings.MILVUS_FIRST_COLLECTION, index_params=index_params
    )


def init_collection():
    create_collection()
    create_index()


init_collection()
