import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

class LLMWrapper:
    def __init__(self, model_id="meta-llama/Llama-4-Scout-17B-16E-Instruct"):
        self.client = InferenceClient(model=model_id, token=HF_TOKEN, timeout=60)

    def summarize_jira_context(self, jira_context: dict) -> str:
        prompt = f"""
You are a senior QA engineer.

Given the following JIRA ticket context, summarize it into a short paragraph describing the purpose, functionality, and scope of the issue:

JIRA Context:
Issue ID: {jira_context['issue_id']}
Summary: {jira_context['summary']}
Description: {jira_context['description']}
Type: {jira_context['issue_type']}
Labels: {', '.join(jira_context['labels'])}
Epic: {jira_context['epic_link']}

Only return the summary text. Do not add labels or explanation.
"""
        response = self.client.text_generation(prompt, max_new_tokens=300, temperature=0.7)
        return response.strip()

    def generate_bdd_feature(self, summarized_context: str) -> str:
        prompt = f"""
You are a QA automation engineer.

Given the following requirement summary, write a BDD feature file using Gherkin syntax.

Summary:
{summarized_context}

Rules:
- Use `Feature:` followed by a meaningful title.
- Include at least two `Scenario:`s.
- Each scenario should contain `Given`, `When`, `Then` steps.
- Only output the .feature content. No comments or explanation.

Output:
"""
        response = self.client.text_generation(prompt, max_new_tokens=500, temperature=0.7)
        return response.strip()
