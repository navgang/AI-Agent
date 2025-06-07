from langchain.agents import initialize_agent, Tool
from openai import OpenAI
from tools import top_companies, stale_connections, craft_message

tools = [
    Tool("top_companies", top_companies, "Top companies in my network."),
    Tool("stale_connections", stale_connections, "Connections older than X years."),
    Tool("craft_message", craft_message, "Draft a LinkedIn note."),
    # Tool("send_message", send_message, "Send the message to a profile.")  # use carefully
]

llm = OpenAI(temperature=0)
agent = initialize_agent(tools, llm, agent="zero-shot-react-description", verbose=True)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("query", help="What do you want to ask your LinkedIn network?")
    args = p.parse_args()
    print(agent.run(args.query))