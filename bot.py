from langchain.agents import initialize_agent, Tool
from langchain.llms.openai import OpenAI
from tools import top_companies, stale_connections

def build_agent(verbose: bool = False):
    """
    Construct and return a LangChain agent wired up
    with your LinkedIn tools.
    """
    llm = OpenAI(temperature=0)
    tools = [
        Tool("top_companies",    top_companies,    "Top companies in my network."),
        Tool("stale_connections",stale_connections,"Connections older than X years.")
    ]
    return initialize_agent(
        tools, 
        llm, 
        agent="zero-shot-react-description", 
        verbose=verbose
    )

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="CLI for your LinkedIn AI agent")
    p.add_argument(
        "query", 
        help="What do you want to ask your LinkedIn network?"
    )
    p.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Show the agent’s reasoning trace"
    )
    args = p.parse_args()

    agent = build_agent(verbose=args.verbose)
    print(agent.run(args.query))