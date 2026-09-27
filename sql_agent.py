import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
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

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

If a query you attempted to run was rejected or not approved, you MUST NOT
guess, estimate, or use general/outside knowledge to answer the question.
Instead, clearly tell the user that you were unable to retrieve the requested
data because query execution was not approved, and stop there.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
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


def ask(question: str, thread_id: str = "default"):
    """Send a question to the agent, handling any human-in-the-loop pause."""
    config = {"configurable": {"thread_id": thread_id}}

    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config,
    )

    while "__interrupt__" in result:
        interrupt = result["__interrupt__"][0]
        for request in interrupt.value["action_requests"]:
            print(f"\n[Approval needed] Tool: {request['name']}")
            print(f"Query: {request['args'].get('query', request['args'])}")

        decision = input("\nApprove this query? (y/n): ").strip().lower()

        if decision == "y":
            result = agent.invoke(
                Command(resume={"decisions": [{"type": "approve"}]}),
                config,
            )
        else:
            result = agent.invoke(
                Command(resume={"decisions": [{"type": "reject"}]}),
                config,
            )

    return result["messages"][-1].content


if __name__ == "__main__":
    print("SQL Agent — type a question, or 'quit' to exit.\n")
    while True:
        question = input("Your question: ").strip()
        if question.lower() in ("quit", "exit"):
            break
        if not question:
            continue
        answer = ask(question, thread_id="interactive-session")
        print(f"\nAnswer: {answer}\n")