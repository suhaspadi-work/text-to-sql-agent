import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

load_dotenv()

db = SQLDatabase.from_uri(os.environ["DATABASE_URL"])
model = init_chat_model("gemini-3.8-flash", model_provider="google_genai")

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

print("Tools available:")
for t in tools:
    print(f" - {t.name}: {t.description[:80]}...")

print()
print("=== Manually testing each tool ===")

# Find each tool by name so we can call them directly
tools_by_name = {t.name: t for t in tools}

# 1. List tables
list_tables_tool = tools_by_name["sql_db_list_tables"]
print("\n[list_tables]")
print(list_tables_tool.invoke(""))

# 2. Get schema for a specific table
schema_tool = tools_by_name["sql_db_schema"]
print("\n[schema for Artist]")
print(schema_tool.invoke("Artist"))

# 3. Query checker
checker_tool = tools_by_name["sql_db_query_checker"]
print("\n[query checker on a deliberately flawed query]")
print(checker_tool.invoke("SELECT * FROM Artist WHERE Name = 'AC/DC'"))

# 4. Execute a real query
query_tool = tools_by_name["sql_db_query"]
print("\n[executing a real query]")
print(query_tool.invoke("SELECT Name FROM Artist LIMIT 5;"))