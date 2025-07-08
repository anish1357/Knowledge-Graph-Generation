import requests
import json
import os
from llm_wrapper import LLMWrapper

class ContextGathererAgent:
    def __init__(self, mcp_url="http://localhost:5000/tool/get_jira_context"):
        self.mcp_url = mcp_url
        self.llm = LLMWrapper()

    def get_jira_context(self, issue_id: str) -> dict:
        response = requests.post(self.mcp_url, json={"issue_id": issue_id})
        response.raise_for_status()
        return response.json()

    def gather_and_summarize(self, issue_id: str) -> dict:
        jira_context = self.get_jira_context(issue_id)
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

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python context_gatherer_agent.py <JIRA_ISSUE_ID>")
    else:
        agent = ContextGathererAgent()
        agent.gather_and_summarize(sys.argv[1])
