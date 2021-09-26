import os

MONGO_QUERY_DB = os.getenv("MONGO_QUERY_DB", 'BOE')
MONGO_HOST = os.getenv("MONGO_HOST", '192.168.1.5')
MONGO_PORT = os.getenv("MONGO_PORT", 27017)

STAGE = os.getenv("STAGE", "dev").lower()

CHILD_QUERY_TABLE = f'{STAGE}_{os.get("CHILD_QUERY_TABLE", "child_table")}'
ADULT_QUERY_TABLE = f'{STAGE}_{os.get("ADULT_QUERY_TABLE", "adult_table")}'
ACCOUNT_QUERY_TABLE = f'{STAGE}_{os.get("ACCOUNT_QUERY_TABLE", "account_table")}'
TASK_QUERY_TABLE = f'{STAGE}_{os.get("TASK_QUERY_TABLE", "task_table")}'
