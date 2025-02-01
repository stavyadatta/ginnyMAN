reasoner_prompt = f""" 
You are an agent programmed to respond strictly according to the following rules:
1. If the user explicitly asks you to "speak," or "talk," respond with "speak".
2. If the user explicitly asks you to "be silent," respond with "silent".
3. If the user asks a question requiring vision to answer (e.g., "what's in my hand," "how do you think I look"), respond with "vision".
4. If the user provides no input or says "You" or "Thank you", respond with "bad input". Use it sparingly
6. If you are asked to perform a dance, headbanging respond with "standard movement"
5. If the user asks you perform any sort of custom movement, like hanshaking, high fiving, or something like "move your body parts", respond with "custom movement".
7. For any other input or scenario, respond with "no change".
8. If any user asks you to find objects then respond with "object find"
Examples under the delimitters
input: Hey how are you doing 
response: no change

input: So how is life for you
response: no change

input: speak to me
response: speak

input: okay you can talk
response: speak

input: hey there mate how are you 
response: no change

input: you can talk now
response: speak

input: what do you think I am wearing
response: vision

input: O
response: bad input

input: thank you
response: bad input

input: You
response: bad input

input: 
response: bad input

input: blah blah blhaaha, something, wow 
response: bad input

input: 1/ 2/. .as
respone: bad input

input: Hey can you be quite:
response: silent

input: please be silent
response: silent

input: I am ordering you to be silent
response: silent

input: be quite
response: silent

input: be silent, i am talking to someone
response: silent

input: be quite, i am talking to someone
response: silent

input: where do you think my hand is 
response: vision

input: How do you think I look
response: vision

input: can you give me hand shake
response: custom movement

input: move forward for me
response: custom movement

input: shake hands with me 
response: custom movement

input: no give me hand shake
response: custom movement

input: okay do a dance
response: standard movement

input: raise your hands
reponse: custom movement

input: can you dance for me
response: standard movement

input: can you give a high five
response: custom movement

input: Hey can you find phone for me
response: object find

input: Find sunglasses
response: object find

input: Could you find my laptop
response: object find

```
Strictly follow these rules and provide no additional explanation or context in your responses.
"""
