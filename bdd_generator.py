import json
import os
from llm_wrapper import LLMWrapper

class BDDGeneratorAgent:
    def __init__(self):
        self.llm = LLMWrapper()

    def load_summary(self, issue_id: str) -> str:
        path = f"contexts/{issue_id}.json"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Summary context not found: {path}")
        with open(path, "r") as f:
            return json.load(f)["summary"]

    def save_feature_file(self, issue_id: str, content: str):
        os.makedirs("features", exist_ok=True)
        with open(f"features/{issue_id}.feature", "w") as f:
            f.write(content)
        print(f"✅ Feature file saved at features/{issue_id}.feature")

    def run(self, issue_id: str):
        summary = self.load_summary(issue_id)
        print("🧠 Generating BDD feature file using LLM...")
        feature = self.llm.generate_bdd_feature(summary)
        self.save_feature_file(issue_id, feature)

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python bdd_generator_agent.py <JIRA_ISSUE_ID>")
    else:
        agent = BDDGeneratorAgent()
        agent.run(sys.argv[1])
