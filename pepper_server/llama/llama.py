import os
from openai import OpenAI

class Llama:
    def __init__(self, llama_url="http://127.0.0.2:8080/v1"):
        """
        Initialize the Llama handler with the llama.cpp server URL.
        :param llama_url: Endpoint of the llama.cpp server.
        """
        self.llama_url = llama_url
        api_key = os.environ["API_KEY"]
        self.client = OpenAI(
            #base_url="http://localhost:8080/v1", 127.0.0.1
            base_url=llama_url,
            api_key = api_key
        )

    def send_to_llama(self, text):
        """
        Send transcribed text to the llama.cpp server and stream its response.
        :param text: Transcribed text to send.
        :return: Generator yielding streamed responses from the llama.cpp server.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Model name; can be any string
                messages=[
                    {"role": "system", "content": "You are a helpful assistant (under 20 words)."},
                    {"role": "user", "content": text}
                ],
                temperature=0.7,  # Adjusts randomness: 0.0 (deterministic) to 1.0 (more random)
                max_tokens=100,   # Maximum number of tokens to generate
                top_p=0.9,         # Nucleus sampling: considers tokens that comprise the top P probability mass
                stream=True        # Enable streaming responses
            )
            print("The response data structure is ", response)
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                     yield chunk.choices[0].delta.content

                # if 'choices' in chunk:
                #     delta = chunk['choices'][0].get('delta', {}).get('content', '')
                #     print("The delta is this ", delta)
                #     if delta:
                #         print("The delta is this ", delta)
                #         yield delta.strip()
        except Exception as e:
            print(f"Error sending to llama.cpp server: {e}")
            yield "Error communicating with llama.cpp server"

    # def send_to_llama(self, text):
    #     """
    #     Send transcribed text to the llama.cpp server and return its response.
    #     :param text: Transcribed text to send.
    #     :return: Response from the llama.cpp server.
    #     """
    #     try:
    #         response = self.client.chat.completions.create(
    #             model="gpt-3.5-turbo",  # Model name; can be any string
    #             messages=[
    #                 {"role": "system", "content": "You are a helpful assistant."},
    #                 {"role": "user", "content": text}
    #             ],
    #             temperature=0.7,  # Adjusts randomness: 0.0 (deterministic) to 1.0 (more random)
    #             max_tokens=500,   # Maximum number of tokens to generate
    #             top_p=0.9,         # Nucleus sampling: considers tokens that comprise the top P probability mass
    #         )
    #         return response.choices[0].message.content.strip()
    #     except Exception as e:
    #         print(f"Error sending to llama.cpp server: {e}")
    #         return "Error communicating with llama.cpp server"
