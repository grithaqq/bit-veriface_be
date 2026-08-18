run-server:
	PYTHONPATH=src/bit_veriface uvicorn main:app --reload --workers 1 --host 0.0.0.0 --port 8005

db-init:
	PYTHONPATH=src/bit_veriface alembic init migrations

db-migrate:
	PYTHONPATH=src/bit_veriface alembic revision --autogenerate
	PYTHONPATH=src/bit_veriface alembic upgrade head

db-prestart:
	PYTHONPATH=src/bit_veriface python ./src/bit_veriface/app_pre_start.py

initial-data:
	PYTHONPATH=src/bit_veriface python ./src/bit_veriface/initial_data.py

collection-init:
	PYTHONPATH=src/bit_veriface python ./src/bit_veriface/dbase/milvus/init_collection.py

precommit:
	pre-commit run --all-files

reseed:
	PYTHONPATH=src/bit_veriface python reset_seed.py
	@echo "Database, Milvus collection, and temporary files have been reset."
	#run db-migrate after reseed to ensure the database schema is up to date
	$(MAKE) db-migrate
	# run collection-init after reseed to ensure the Milvus collection is re-initialized
	$(MAKE) collection-init
	# run initial-data after reseed to ensure the initial data is re-populated
	$(MAKE) initial-data
