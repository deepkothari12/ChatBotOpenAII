from openai import OpenAI

def gpt_models(messages_list, prompt=None):
    client = OpenAI(
        base_url="https://router.huggingface.co/v1",
    )
    
    api_messages = []
    if prompt:
        api_messages.append({"role": "system", "content": prompt})
    
    # Add all the conversation messages
    api_messages.extend(messages_list)
    
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b:novita",
        messages=api_messages,
        stream=True
    )
    # print("------------------>>>>>>>" , completion)
    return completion #.choice[0].delta.content

gpt_models([{"role": "user", "content": "Hello!"}])