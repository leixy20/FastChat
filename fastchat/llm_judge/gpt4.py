import time
import json
import multiprocessing
import requests
import openai
from openai.util import convert_to_openai_object

openai.api_base = "http://40.74.217.35:3000/v1"
openai.api_key = "sk-QTbmwUB6eYjigT9Y02Ef8d8366Db4c74BfBc2467Ef5834A7"

def call_gpt4(prompt,
            temperature=0.95,
            model="gpt-4",
            top_p=0.9):
    start_time = time.time()

    # send a ChatCompletion request to count to 100
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {'role': 'user', 'content': prompt}
        ],
        top_p=top_p,
        temperature=temperature,
        stream=True  # again, we set stream=True
    )

    # # local gpt4 api
    # model = "gpt-4"
    # url = "http://40.74.217.35:3000/v1/chat/completions"
    # messages = [{"role":"user", "content":prompt}]
    # payload = json.dumps({
    #     "model": model,
    #     "messages": messages,
    #     "temperature": temperature,
    #     "max_tokens": 512,
    #     "stream": True
    # })
    # headers = {
    #     'Content-Type': 'application/json',
    #     'Authorization': 'sk-QTbmwUB6eYjigT9Y02Ef8d8366Db4c74BfBc2467Ef5834A7'
    # }

    # response = requests.request("POST", url, headers=headers, data=payload, stream=True)

    # chunks = [convert_to_openai_object(line) for line in response]
    # for chunk in chunks:
    #     print("bp1: ", chunk)

    # create variables to collect the stream of chunks
    collected_chunks = []
    collected_messages = []
    # iterate through the stream of events
    for chunk in response:
        chunk_time = time.time() - start_time  # calculate the time delay of the chunk
        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk['choices'][0]['delta']  # extract the message
        collected_messages.append(chunk_message)  # save the message
        print(f"Message received {chunk_time:.2f} seconds after request: {chunk_message}", flush=True)  # print the delay and text

    # print the time delay and text received
    print(f"Full response received {chunk_time:.2f} seconds after request", flush=True)
    full_reply_content = ''.join([m.get('content', '') for m in collected_messages])
    print(f"Full conversation received: {full_reply_content}", flush=True)

    reply = {"prompt": prompt,"reply":full_reply_content}
    
    return reply
    # except Exception as e:
    #     print(e, flush=True)
    #     return {"prompt": prompt,"reply":'', 'err': str(e)}

if __name__ == "__main__":
    prompt = "Introduce yourself."
    print(call_gpt4(prompt))