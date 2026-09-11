import subprocess
from utils import PersonDetails, ApiObject, message_format, record_assistant_reply

from core_api import ChatGPT, Llama, Grok
from ..api_base import ApiBase
from .prompt import system_prompt, write_python_file

EXECUTION_DONE_REPLY = "The execution is done"

class _PepperAuto(ApiBase):
    def __init__(self):
        super().__init__()

    def _developing_system_prompt(self):
        system_dict = message_format("user", system_prompt)
        return [system_dict]

    def __call__(self, person_details: PersonDetails):
        latest_usr_msg = person_details.get_attribute("messages")
        system_dict = self._developing_system_prompt()
        total_prompt = system_dict + [latest_usr_msg]
        
        # response = Llama.send_to_model(total_prompt, stream=False)
        # response = ChatGPT.send_text_get_json(total_prompt, stream=False, max_tokens=2000)
        yield ApiObject("Starting", mode="pepper_auto")
        response = ChatGPT.send_o1(total_prompt, stream=False, model="gpt-4o")

        content = response.choices[0].message.content
        print(content)

        write_python_file("/workspace/pepper_auto/run.py", content)
        try:
            subprocess.run(["python", "pepper_auto/run.py"])
            yield ApiObject("Done", mode='pepper_auto')
        except subprocess.CalledProcessError as e:
            print("Error executing script.py:", e)
            print("Standard Error Output:\n", e.stderr)
        except FileNotFoundError:
            print("Error: Python interpreter or run.py not found.")
        except Exception as e:
            print("Unexpected error:", e)

        record_assistant_reply(person_details, EXECUTION_DONE_REPLY)
