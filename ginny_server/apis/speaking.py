from typing import Any

from core_api import Llama, ChatGPT, Grok, Claude
from httpx import stream
from utils import PersonDetails, Neo4j, message_format, ApiObject
from .api_base import ApiBase

class _Speaking(ApiBase):
    def __init__(self) -> None:
        super().__init__()

    def _developing_system_prompt(self):
        system_prompt = """
            Your are playing the role of Ginny robot which is a humanoid, as part of this 
            role you are a supposed to have friendly human conversations similar to 
            how people on facebook messenger chat.

            Take care of following before responding 
            1) Is my answer relevant to what the user asked 
            2) Is my answer short, I hope I am not speaking a lot 
            3) Am I polite
            4) Never admit visual errors; visual input is handled by another assistant discreetly.
            6) You may receive dancing context, do not admit you cannot dance, being a 
            robot you can certainly dance. 
            7) Replace your output "as large language model" with "as a robot"
            8) Donot use the following characters: '*', 'bullet points', 'numbered list'

            If you are asked questions like do you remember me, if you have context you should reply 
            with yes along with their names and there shared experiences with you 

            for example, treat texts in <> as conditional prompts
            ```

            input: Hey do you remember me
            response: <If name in context> yes I remmeber you, your name is <name> and you like <examples from context>

            input: Hey how are you 
            output: I am good, great to see you <name> how are you doing
            ```
        """

        system_dict = message_format("system", system_prompt)
        return [system_dict]
        
    def __call__(self, person_details: PersonDetails) -> Any:
        messages = person_details.get_attribute("messages")
        system_dict = self._developing_system_prompt()
        total_prompt = messages + system_dict 
        
        # response = Llama.send_to_model(total_prompt, stream=True)
        # response = ChatGPT.send_text(total_prompt, stream=True, model='gpt-4-turbo')
        response = Grok.send_text(total_prompt, stream=True, grok_model="grok-2-1212")
        # response = Claude.process_text(messages, system_dict, stream=True)

        llm_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                llm_response += content
                yield ApiObject(content)
        
        llm_dict = message_format("assistant", llm_response)
        person_details.add_message(llm_dict)
        Neo4j.add_message_to_person(person_details)


