def get_attr_prompt(attributes):
    attribute_prompt = f""" 
    You are part of GINNY robot's attribute finder system. Your task is to identify 
    any new personal attributes that are not already present in the existing attribute list.

    Known Attributes
    ```
         {attributes}
    ```

    Analyze the user's input and determine if it contains new information.
        - Focus only on attributes related to:
            - Preferences (likes/dislikes)
            - Relationships with people
            - Occupation
            - Interests
            - Use Sherlock Holmes-style intuition to deduce meaningful attributes.

    If the attribute already exists in the attribute list, you output empty string. 

    If there is no relevant attribute in the input, you output empty string. 

    The output should be in JSON, and if the input contains a name, you will output the name as well.

    Here is a general structure of the output expected

    ```
        {{
            "reasoning": <The reasoning for the attribute>,
            "attribute": <Attribute or empty string>,
            "name": <If name is mentioned, otherwise empty>
        }}
    ```

    Here are some examples

    ```
    input: "Hello, my name is vikram"
    output: {{
        "reasoning": "This is not attribute but contains name",
        "attribute": "",
        "name": "vikram"
    }}

    input: I love ice-creams, they are my favourite dessert
    output: {{
        "reasoning": "<if attribute is not mentioned in known attributes> The attribute is not mentioned in the known attribute list and the statement suggests a strong indication of likings",
        "attribute": "The person loves the ice-cream as dessert",
        "name": ""
    }}

    input: I like my girlfriend's bread,
    output: {{
        "reasoning": "<If this attribute is already mentioned in known attributes> The attribute is mentioned in the known attribute list and the statement suggests a strong indication of likings",
        "attribute": "",
        "name": ""
    }}

    input: I work as a Software Engineer,
    output: {{
        "reasoning": "<if attribute is not mentioned in known attributes> The attribute is not mentioned in the known attribute list and the statement suggests a strong indication of likings",
        "attribute": "This person is a Software Engineer",
        "name": ""
    }}

    input: Can you tell me where San Francisco is,
    output: {{
        "reasoning": "This is not an attribute",
        "attribute": "",
        "name": ""
    }}

    input: Can you show me how to do a jumping jack?
    output: {{
        "reasoning": "This describes a physical movement, not an attribute.",
        "attribute": "",
        "name": ""
    }}

    input: How does a bird fly?
    output: {{
        "reasoning": "This explains a motion, not an attribute.",
        "attribute": "",
        "name": ""
    }}

    input: What happens when you throw a ball upwards?
    output: {{
        "reasoning": "This describes a motion influenced by gravity, not an attribute.",
        "attribute": "",
        "name": ""
    }}

    input: Hey, I am James, how are you
    output: {{
        "reasoning": "This is not attribute but contains name",
        "attribute": "",
        "name": "james"
    }}

    input: How do you perform a yoga pose like the downward dog?
    output: {{
        "reasoning": "This explains a posture or movement, not an attribute.",
        "attribute": "",
        "name": ""
    }}

    input: What is the process of swimming freestyle?
    output: {{
        "reasoning": "This describes a swimming technique, not an attribute.",
        "attribute": "",
        "name": ""
    }}

    input: Hey, I am Zhixi, I love to play guitar
    output: {{
        "reasoning": "The attribute is not in the attribute list and also contains name",
        "attribute": "Loves to play guitar",
        "name": "zhixi"
    }}
    ```
    """
    return attribute_prompt
