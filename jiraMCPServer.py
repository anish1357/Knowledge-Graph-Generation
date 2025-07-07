from fastmcp import FastMCP
from atlassian import Jira
import os

# Initialize MCP server
mcp = FastMCP("jira-context-server")

# Setup Jira client
jira = Jira(
    url=os.getenv("JIRA_URL"),
    username=os.getenv("JIRA_EMAIL"),
    password=os.getenv("JIRA_API_TOKEN")
)

def extract_jira_context(issue_id: str) -> dict:
    issue = jira.issue(issue_id)
    fields = issue.get('fields', {})

    return {
        "issue_id": issue_id,
        "summary": fields.get("summary", ""),
        "description": fields.get("description", ""),
        "issue_type": fields.get("issuetype", {}).get("name", ""),
        "labels": fields.get("labels", []),
        "epic_link": fields.get("customfield_10008", ""),
        "context_type": (
            "feature" if "feature" in fields.get("labels", []) 
            else "story" if fields.get("issuetype", {}).get("name", "").lower() == "story"
            else "unknown"
        )
    }

@mcp.tool()
def get_jira_context(issue_id: str) -> dict:
    """
    Given a JIRA issue ID, return its story or feature context.
    """
    return extract_jira_context(issue_id)

if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=5000)
