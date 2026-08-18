from dbase.milvus.connection import DataType, MilvusClient

schema = MilvusClient.create_schema()

schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
schema.add_field("vector", DataType.FLOAT_VECTOR, dim=128)
schema.add_field("img_path", DataType.VARCHAR, max_length=256)
schema.add_field("img_id", DataType.VARCHAR, max_length=256)
schema.add_field("user_id", DataType.VARCHAR, max_length=256)
