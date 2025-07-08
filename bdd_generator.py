import requests
import os
import json

HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

HEADERS = {
    "Authorization": f"Bearer {HUGGINGFACE_TOKEN}",
    "Content-Type": "application/json"
}

MCP_SERVER_URL = "http://localhost:5000/tool/get_jira_context"

def get_jira_context(issue_id: str) -> dict:
    response = requests.post(MCP_SERVER_URL, json={"issue_id": issue_id})
    response.raise_for_status()
    return response.json()

def generate_bdd_from_context(context: dict) -> str:
    """
    Call Hugging Face model to generate BDD feature from JIRA context.
    """
    prompt = f"""
You are a software QA expert. Given the following JIRA issue details:

- Issue ID: {context['issue_id']}
- Summary: {context['summary']}
- Description: {context['description']}
- Type: {context['issue_type']}
- Labels: {', '.join(context['labels'])}
- Epic: {context['epic_link']}

Write a BDD feature file in Gherkin format.
Include a `Feature:` title and at least two `Scenario:` examples with `Given`, `When`, `Then` steps.
Return only the .feature file content.
"""

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 500,
            "temperature": 0.7,
            "return_full_text": False
        }
    }

    response = requests.post(HUGGINGFACE_API_URL, headers=HEADERS, json=payload)
    response.raise_for_status()
    result = response.json()

    # Depending on model, may return a list or string
    if isinstance(result, list):
        return result[0]["generated_text"].strip()
    elif isinstance(result, dict) and "generated_text" in result:
        return result["generated_text"].strip()
    else:
        raise ValueError("Unexpected response from Hugging Face API")

def save_bdd_to_file(feature_text: str, issue_id: str):
    filename = f"{issue_id}.feature"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(feature_text)
    print(f"✅ BDD feature file saved as: {filename}")

def run_bdd_agent(issue_id: str):
    print(f"🔍 Fetching context for: {issue_id}")
    context = get_jira_context(issue_id)
    print(f"📘 Context received: {json.dumps(context, indent=2)}")

    print("🧠 Generating BDD Feature File using Hugging Face LLM...")
    feature_text = generate_bdd_from_context(context)

    print("💾 Saving feature file...")
    save_bdd_to_file(feature_text, issue_id)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python bdd_generator_agent_hf.py <JIRA_ISSUE_ID>")
    else:
        run_bdd_agent(sys.argv[1])
