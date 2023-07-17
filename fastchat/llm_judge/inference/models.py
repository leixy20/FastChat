import jsonlines
import requests
import json
import pandas as pd
import random
from tqdm import tqdm
from typing import List
import threading
from utils import SSEClient

class api_model:
    def __init__(self, workers=20):
        self.workers = workers

    def call_api_in_parallel(self, prompts, workers: int, timeout: int = 180) -> List[str]:

        def get_result_with_retry(prompt, retries=3, timeout=timeout): # TODO retries
            for attempt in range(retries):
                result = [None]
                timeout_event = threading.Event()

                def target():
                    try:
                        result[0] = self.get_api_result(prompt)
                    except Exception as e:
                        print(f"Error occurred while fetching results for prompt: {e}")
                        result[0] = None
                    finally:
                        timeout_event.set()

                worker = threading.Thread(target=target)
                worker.start()

                if not timeout_event.wait(timeout):
                    print(f"Timeout occurred while fetching results for prompt (attempt {attempt + 1})")
                else:
                    break

            return result[0]

        def worker_thread(prompt, index, results):
            results[index] = get_result_with_retry(prompt)

        threads = []
        results = [None] * len(prompts)

        for index, data in tqdm(enumerate(prompts)):
            prompt = data
            t = threading.Thread(target=worker_thread, args=(prompt, index, results))
            t.start()
            threads.append(t)

            if len(threads) >= workers:
                threads[0].join()
                threads.pop(0)

        for t in threads:
            t.join()

        return results

    def generate_text(self, dataset):
        result = self.call_api_in_parallel(dataset, self.workers)
        return result

    def get_api_result(self, prompt):
        pass

class ChatGLM2(api_model):
    def __init__(self, workers = 10):
        self.url = "" # TODO
        self.temperature = 0.95
        self.max_tokens = 10
        self.workers = workers

    def get_api_result(self, prompt):
        url = self.url

        payload = json.dumps({
            "prompt": prompt,
            "history": [],
        })
        headers = {
            'Authorization': '', # TODO
            'Content-Type': 'application/json; charset=utf-8'
        }
        response = requests.request("POST", url, headers=headers, data=payload, stream=True)
        client = SSEClient(response)
        for event in client.events():
            if event.event == "add":
                continue
            elif event.event == "finish":
                return event.data
        return None

class ChatGPT(api_model):
    def __init__(self, workers=10):
        self.url = "" # TODO
        self.model = "gpt-3.5-turbo"
        self.workers = workers

    def get_api_result(self, prompt):
        url = self.url

        payload = json.dumps({
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': '', # TODO
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text).get("choices")[0].get("message").get("content")

class ChatGLM2_6B(api_model):
    def __init__(self, workers=10):
        self.url = "" # TODO
        self.workers = workers
        self.timeout = 120

    def get_api_result(self, prompt):
        history = [{"role":"user", "content":prompt}]
        headers = {
            'Authorization': '', # TODO
            'Content-Type': 'application/json'
        }
        resp = requests.post(self.url, json={
            "messages": history,
        }, headers=headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise Exception(f"Invalid status code {resp.status_code}:\n\n{resp.text}")
        try:
            return json.loads(resp.text).get("result", "ERROR")
        except:
            raise Exception(f"Invalid response:\n\n{resp.text}")

class ChatGLM_6B_v1(api_model):
    def __init__(self, workers=10):
        self.url = "" # TODO
        self.workers = workers
        self.timeout = 120

    def get_api_result(self, prompt):
        history = [{"role":"user", "content":prompt}]
        headers = {
            'Authorization': '', # TODO
            'Content-Type': 'application/json'
        }
        resp = requests.post(self.url, json={
            "messages": history,
        }, headers=headers, timeout=self.timeout)
        if resp.status_code != 200:
            raise Exception(f"Invalid status code {resp.status_code}:\n\n{resp.text}")
        try:
            return json.loads(resp.text).get("result", "ERROR")
        except:
            raise Exception(f"Invalid response:\n\n{resp.text}")

def get_model_api(model, workers):
    if model == "ChatGLM2":
        return ChatGLM2(workers)
    if model == "ChatGLM2_6B":
        return ChatGLM2_6B(workers)
    if model == "ChatGLM_6B_v1":
        return ChatGLM_6B_v1(workers)
    if model == "ChatGPT":
        return ChatGPT(workers)
    return None
