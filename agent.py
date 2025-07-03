import os
import ast
import tempfile
import shutil
import stat
import re
from git import Repo  # Use GitPython
from llm import LLMWrapper
from graph_builder import KnowledgeGraphBuilder

class KnowledgeGraphAgent:
    def __init__(self, repo_path_or_url):
        self.temp_dir = None
        if (
            repo_path_or_url.startswith("http://")
            or repo_path_or_url.startswith("https://")
            or repo_path_or_url.endswith(".git")
        ):
            # Clone the GitHub repo to a temp directory using GitPython
            self.temp_dir = tempfile.mkdtemp()
            print(f"[INFO] Cloning repository {repo_path_or_url} to {self.temp_dir} ...")
            Repo.clone_from(repo_path_or_url, self.temp_dir)
            self.repo_path = self.temp_dir
        else:
            self.repo_path = repo_path_or_url
        print(f"[INFO] Repository path set to: {self.repo_path}")
        self.llm = LLMWrapper()
        self.graph_builder = KnowledgeGraphBuilder()

    def process_file(self, file_path):
        print(f"[INFO] Reading file: {file_path}")
        with open(file_path, "r") as f:
            code = f.read()

        print(f"[INFO] Sending code to LLM (length: {len(code)} chars)...")
        response = self.llm.extract_triplets(code)
        print(f"[INFO] Received response from LLM.")
        print(f"[DEBUG] Raw LLM response:\n{response}")

        try:
            # Extract the first Python list from the LLM output using regex
            match = re.search(r"\[\s*\([^\]]+\)\s*(?:,\s*\([^\]]+\)\s*)*\]", response, re.DOTALL)
            if match:
                triplet_str = match.group(0)
                triplets = ast.literal_eval(triplet_str)
                print(f"[INFO] Parsed {len(triplets)} triplets from LLM output.")

                # Visualize before persisting
                self.graph_builder.visualize_triplets(triplets)

                for subject, relation, object_ in triplets:
                    print(f"[INFO] Adding triplet: ({subject}, {relation}, {object_})")
                    self.graph_builder.add_triplet(subject, relation, object_)
            else:
                print(f"[ERROR] No valid triplet list found in LLM output:\n{response}")
        except Exception as e:
            print(f"[ERROR] Error parsing LLM output: {e}\nOutput was:\n{response}")

    def run(self):
        print(f"[INFO] Starting to walk through repository: {self.repo_path}")
        java_file_count = 0
        for dirpath, _, files in os.walk(self.repo_path):
            for file in files:
                if file.endswith(".java"):
                    java_file_count += 1
                    print(f"[INFO] Processing Java file #{java_file_count}: {os.path.join(dirpath, file)}")
                    self.process_file(os.path.join(dirpath, file))
        print(f"[INFO] Finished processing {java_file_count} Java files.")
        if self.temp_dir:
            print(f"[INFO] Cleaning up temporary directory {self.temp_dir}...")
            shutil.rmtree(self.temp_dir, onerror=remove_readonly)

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)
