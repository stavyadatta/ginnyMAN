import requests

class Llama:
    def __init__(self, llama_url="http://172.27.72.27:8080/api/chat"):
        """
        Initialize the Llama handler with the llama.cpp server URL.
        :param llama_url: Endpoint of the llama.cpp server.
        """
        self.llama_url = llama_url

    def send_to_llama(self, text):
        """
        Send transcribed text to the llama.cpp server and return its response.
        :param text: Transcribed text to send.
        :return: Response from the llama.cpp server.
        """
        try:
            response = requests.post(
                self.llama_url,
                json={"message": text},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("response", "No response from llama.cpp")
        except requests.RequestException as e:
            print(f"Error sending to llama.cpp server: {e}")
            return "Error communicating with llama.cpp server"
