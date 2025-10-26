from .api import Api
import requests
import os
import json

class GenAiChatApi(Api):
    """
    A specialized API client for interacting with a GenAI Chat Completions endpoint.

    Inherits from the base Api class and simplifies sending chat prompts.

    Attributes:
        model (str): The name of the model to use for chat completions.
    """
    CHAT_ENDPOINT = "/api/chat/completions"
    _TIMEOUT = 60.0


    def __init__(self, base_url: str, model: str):
        """
        Initializes the GenAiChatApi client.

        Args:
            base_url (str): The base URL for the API (e.g., "https://genai.rcac.purdue.edu").
            model (str): The model identifier (e.g., "llama3.1:latest").
        """
        super().__init__(base_url)
        self.model = model
        #print(f"Chat client initialized for model: {self.model}")

    def get_chat_completion(self, content: str) -> str:
        """
        Sends a message to the chat API and returns the assistant's text response.

        Args:
            content (str): The user's message content.

        Returns:
            Optional[str]: The text content of the model's reply, or None if not found.
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": content}],
            "stream": False
        }

        try:
            # Call the parent class's post method
            response_data = self.post(endpoint=self.CHAT_ENDPOINT, payload=payload)

            # If API returned raw JSON text, parse it
            if isinstance(response_data, str):
                try:
                    response_data = json.loads(response_data)
                except Exception:
                    return ""  # bad JSON → no content

            # Only proceed if we have a dict (mapping)
            if isinstance(response_data, dict):
                choices = response_data.get("choices")
                if isinstance(choices, list) and choices:
                    first_choice = choices[0]
                    if isinstance(first_choice, dict):
                        message = first_choice.get("message")
                        if isinstance(message, dict):
                            text = message.get("content")
                            return text if isinstance(text, str) else ""

            # If structure is not as expected
            return ""

        except Exception:
            return ""

def main():
    """
    Example of how to use the GenAiChatApi class from its new module.
    """
    api_key = os.getenv("API_KEY")
    if not api_key:
        print("Error: API_KEY environment variable not set.")
        return

    # Initialize the client
    chat_api = GenAiChatApi(
        base_url="https://genai.rcac.purdue.edu",
        model="llama3.1:latest"
    )

    # Set the token
    chat_api.set_bearer_token(api_key)

    # Get a completion
    prompt = "What are the three most important things to know about Python classes?"
    print(f"\n> Sending prompt: '{prompt}'")
    
    response_text = chat_api.get_chat_completion(prompt)

    # Print the result
    if response_text:
        print("\n--- Model Response ---")
        print(response_text)
        print("----------------------")
    else:
        print("\nFailed to get a response from the model.")

if __name__ == "__main__":
    main()