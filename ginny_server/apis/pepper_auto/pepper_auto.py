import subprocess
from utils import PersonDetails, Neo4j, message_format, ApiObject

from core_api import ChatGPT, Llama, Grok
from ..api_base import ApiBase
from .prompt import system_prompt, write_python_file

class _PepperAuto(ApiBase):
    def __init__(self):
        super().__init__()

    def _developing_system_prompt(self):
        system_dict = message_format("system", system_prompt)
        return [system_dict]

    def __call__(self, person_details: PersonDetails):
        messages = person_details.get_attribute("messages")
        system_dict = self._developing_system_prompt()
        total_prompt = system_dict + [messages[-1]]
        
        # response = Llama.send_to_model(total_prompt, stream=False)
        # response = ChatGPT.send_text_get_json(total_prompt, stream=False, max_tokens=2000)
        yield ApiObject("Starting", stream=False, mode="pepper_auto")
        response = ChatGPT.send_text(total_prompt, stream=False, max_tokens=5000, model="o3-mini")

        content = response.choices[0].message.content
        print(content)

        write_python_file("/workspace/ginnyMAN/pepper_auto/run.py", content)
        try:
            subprocess.run(["python", "pepper_auto/run.py"])
            yield ApiObject("Done", stream=False, mode='pepper_auto')
        except subprocess.CalledProcessError as e:
            print("Error executing script.py:", e)
            print("Standard Error Output:\n", e.stderr)
        except FileNotFoundError:
            print("Error: Python interpreter or run.py not found.")
        except Exception as e:
            print("Unexpected error:", e)

        llm_dict = message_format("assistant", "The execution is done")
        person_details.add_message(llm_dict)
        person_details.set_attribute("state", "speak")
        Neo4j.add_message_to_person(person_details)
