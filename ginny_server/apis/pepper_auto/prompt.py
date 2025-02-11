def read_python_file(file_path):
    """Reads a Python file and returns its content as a string."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None


def write_python_file(file_path, content):
    """Writes content to a Python file while preserving indentation."""
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)
    except Exception as e:
        print(f"Error writing file: {e}")


boilerplate = read_python_file("/workspace/pepper_auto/boilerplate.py")
yolo_world = read_python_file("/workspace/ginny_server/core_api/yolo/yolo_world.py")
chatgpt = read_python_file("/workspace/ginny_server/core_api/chatgpt/chatgpt.py")
grok = read_python_file("/workspace/ginny_server/core_api/grok/grok.py")
pepper_proto = read_python_file("/workspace/grpc_communication/pepper_auto.proto")

system_prompt = f"""
You are given a prompt by the user, now you need to develop the code in python for the user's 
usecase. You should only respond with the code and nothing else, all the comments and 
reasoning should be done within the python script as comments. 

While generating code you need to use the boilerplate within the delimitters

```
{boilerplate}
```

You can use the following apis to assist you 

ChatGPT (use the img_text_response) for generating a response
```
{chatgpt}
```

Grok (use the img_text_response) for generating a response

```
{grok}
```

yolo_world

```
{yolo_world}
```

pepper robot controls 
```
{pepper_proto}
```

The class variables are already declared within the boilerplate and therefore the 
methods can be accessed

The pepper robot can be used by the stub that has been declared, please 
note the names of  the joints in the pepper robot proto file
"""

if __name__ == "__main__":
    file_path = "/workspace/pepper_auto/test.txt"
    write_python_file(file_path, system_prompt)
