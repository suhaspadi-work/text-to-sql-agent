import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit

load_dotenv()

db = SQLDatabase.from_uri(os.environ["DATABASE_URL"])
model = init_chat_model("gemini-3.5-flash-lite", model_provider="google_genai")

toolkit = SQLDatabaseToolkit(db=db, llm=model)
tools = toolkit.get_tools()

system_prompt = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.
""".format(dialect=db.dialect, top_k=5)

agent = create_agent(
    model,
    tools,
    system_prompt=system_prompt,
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"sql_db_query": True},
            description_prefix="Tool execution pending approval",
        ),
    ],
    checkpointer=InMemorySaver(),
)

if __name__ == "__main__":
    question = "Which genre on average has the longest tracks?"
    config = {"configurable": {"thread_id": "test-1"}}

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config,
    )

    # Check whether execution paused for approval
    if "__interrupt__" in result:
        print("=== INTERRUPTED — awaiting human approval ===")
        interrupt = result["__interrupt__"][0]
        for request in interrupt.value["action_requests"]:
            print(f"Tool: {request['name']}")
            print(f"Args: {request['args']}")
        print(f"\nAllowed decisions: {interrupt.value['review_configs'][0]['allowed_decisions']}")
        print("\n(Execution paused. Nothing has run yet against the database.)")
        
        from langgraph.types import Command
        print("\n=== Resuming with approval ===")
        resumed_result = agent.invoke(
            Command(resume={"decisions": [{"type": "approve"}]}),
            config,
        )
        print("\n=== Final answer after approval ===")
        print(resumed_result["messages"][-1].content)
    else:
        print("=== No interrupt triggered — check middleware config ===")
        print(result["messages"][-1].content)