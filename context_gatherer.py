import asyncio
import json
import os
from llm_wrapper import LLMWrapper
from fastmcp import Client

class ContextGathererAgent:
    def __init__(self, mcp_server="jira-context-server"):
        self.client = Client(mcp_server)
        self.llm = LLMWrapper()

    async def get_jira_context(self, issue_id: str) -> dict:
        async with self.client:
            result = await self.client.call_tool("get_jira_context", {"issue_id": issue_id})
            return result

    async def gather_and_summarize(self, issue_id: str) -> dict:
        jira_context = await self.get_jira_context(issue_id)

        print("🧠 Summarizing JIRA context using LLM...")
        summary = self.llm.summarize_jira_context(jira_context)

        result = {
            "issue_id": issue_id,
            "summary": summary
        }

        os.makedirs("contexts", exist_ok=True)
        with open(f"contexts/{issue_id}.json", "w") as f:
            json.dump(result, f, indent=2)

        print(f"✅ Context summary saved to contexts/{issue_id}.json")
        return result

# Entry point
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python context_gatherer_agent.py <JIRA_ISSUE_ID>")
        exit(1)

    issue_id = sys.argv[1]
    agent = ContextGathererAgent()

    # Run the async logic synchronously
    asyncio.run(agent.gather_and_summarize(issue_id))
