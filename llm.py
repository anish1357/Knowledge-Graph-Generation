import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

class LLMWrapper:
    def __init__(self, model_id="meta-llama/Llama-4-Scout-17B-16E-Instruct"):
        self.client = InferenceClient(
            provider="fireworks-ai",
            api_key=HF_TOKEN,
        )
        self.model_id = model_id

    def extract_triplets(self, java_code: str) -> str:
        prompt = f"""
    You are an expert in Java and software architecture. Given the following Java file, extract only the relationships (such as extends, implements, calls, dependencies) between classes that are defined within this source code. Exclude any relationships involving classes from Java standard libraries (e.g., java.util.*) or any external/third-party dependencies. Only include relationships where both classes are defined in the provided code.
    If there are no relationships, return an empty list. Dont reply with explaination texts just return the lists in the format specified below.
    Classify the relationships as follows:
    - "extends" for inheritance relationships
    - "implements" for interface implementation relationships
    - "calls" for method calls between classes
    - "depends_on" for dependencies between classes

    Only Consider the Java classes related to APIs
    - Controller classes
    - Service classes    
    - Repository classes
    - Model classes
    - DTO classes
    - Utility classes
    - Exception classes

    Exclude any third-party libraries or frameworks and test classes.
    Java Code:
    {java_code}

    Output format (Python list of tuples):
    [("ClassA", "extends", "ClassB"), ("ClassA", "calls", "ClassB.methodX")]
    """
        completion = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
        )
        return completion.choices[0].message["content"]