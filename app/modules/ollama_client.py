import requests

OLLAMA_URL = "http://172.30.32.1:11434/api/generate"

MODEL_NAME = "llama3.2:1b"


def ask_llm(prompt: str) -> str:
    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "num_predict": 350
                }
            },
            timeout=180
        )

        response.raise_for_status()
        data = response.json()
        return data.get("response", "No response returned from Ollama.")

    except Exception as e:
        return f"Ollama error: {str(e)}"