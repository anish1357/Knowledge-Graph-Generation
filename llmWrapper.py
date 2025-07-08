import os
from huggingface_hub import InferenceClient

HF_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

class LLMWrapper:
    def __init__(self, model_id="meta-llama/Llama-4-Scout-17B-16E-Instruct"):
        self.client = InferenceClient(model=model_id, token=HF_TOKEN, timeout=60)

    def summarize_jira_context(self, jira_context: dict) -> str:
        prompt = f"""
You are a senior QA automation engineer helping translate JIRA tickets into executable BDD scenarios.

Below are two JIRA items:
1. A **story**, which defines the business requirement or user goal.
2. A **feature**, which defines the technical implementation or functionality supporting the story.

Your task is to combine both into **one concise summary paragraph** that:
- Clearly describes the end-to-end functionality.
- Covers the purpose, flow, and expected outcome.
- Is neutral, clear, and written for engineers or test automation.
- Avoids redundant rephrasing.

Do NOT add headings, markdown, or any explanation.

---
Story:
- Key: {jira_context.get('key')}
- Summary: {jira_context.get('summary')}
- Description: {jira_context.get('description')}
- Accecptance Criteria: {jira_context.get('acceptance_criteria', '')}

Feature:
- Key: {jira_context.get('key')}
- Summary: {jira_context.get('summary')}
- Description: {jira_context.get('description')}
- Accecptance Criteria: {jira_context.get('acceptance_criteria', '')}

---
Output Format:
Return a single paragraph summary describing the complete flow of the functionality, combining both story and feature.
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
