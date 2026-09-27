import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase

load_dotenv()

db_url = os.environ["DATABASE_URL"]
db = SQLDatabase.from_uri(db_url)

print("Dialect:", db.dialect)
print("Usable tables:", db.get_usable_table_names())
print()
print("Schema info for 'Artist' table:")
print(db.get_table_info(["Artist"]))