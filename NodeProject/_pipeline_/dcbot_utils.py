# -*- coding: utf-8 -*-
import os, csv, os, json, time, pprint, sys, shutil, random, traceback, requests
import system_manager
import production_manager
from notionDatabase import notionDatabase as ntdb

base_path = os.path.dirname(os.path.abspath(__file__))


class chatgpt:
    def __init__(self):
        self.dc_cfg_path = os.path.join(base_path, "raspi_dcbot.json")
        self.dc_cfg = json.load(open(self.dc_cfg_path))
        # self.dc_cfg["open_ai_gpt"]["model"] = "gpt-3.5-turbo"
        self.dc_cfg["open_ai_gpt"]["model"] = "gpt-4o-mini"
        self.client = system_manager.chatgpt_client(
            model=self.dc_cfg["open_ai_gpt"]["model"],
            api_key=self.dc_cfg["open_ai_gpt"]["api_key"],
        )
        self.system_dict = {
            "general": {
                "role": "system",
                "content": (
                    "You are a helpful assistant. you will say straightforward\n"
                    "avoiding indirect language. \n"
                    "listing out  can be easily to read and understand\n"
                    "Your format to reply will be on 'Discord' and you must have Markdown code block eg ```your code/your paragraph```\n"
                ),
            },
            "": "",
            # "" : "",
        }

    def chat(self, **kwargs):
        self.client.chat(**kwargs)
        result = self.client.chat(**kwargs)
        return result


import websocket, uuid
import urllib.request
import urllib.parse
import urllib.error

"""
class comfy_ui:
    def __init__(
        self,
        server="127.0.0.1:8188",
        ws_timeout=60,
    ):
        self.server = server.rstrip("/")
        self.ws_url = (
            self.server.replace("http://", "")
            .replace("https://", "")
            .replace("http", "ws")
        )
        self.ws_timeout = ws_timeout
        self.client_id = str(uuid.uuid4())
        self.ws = websocket.WebSocket()

    def socket_connect(self):
        self.ws.connect("ws://{}/ws?clientId={}".format(self.ws_url, self.client_id))

    def socket_close(self):
        self.ws.close()

    def get_queue_prompt(self, prompt, prompt_id):
        p = {"prompt": prompt, "client_id": self.client_id, "prompt_id": prompt_id}
        data = json.dumps(p).encode("utf-8")
        req = urllib.request.Request("http://{}/prompt".format(self.server), data=data)
        try:
            resp = urllib.request.urlopen(req)
            body = resp.read().decode()
            return resp.getcode(), body
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            return e.code, error_body

    def get_image(self, filename, subfolder, folder_type):
        data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
        url_values = urllib.parse.urlencode(data)
        with urllib.request.urlopen(
            "http://{}/view?{}".format(self.server, url_values)
        ) as response:
            return response.read()

    def get_history(self, prompt_id):
        with urllib.request.urlopen(
            "http://{}/history/{}".format(self.server, prompt_id)
        ) as response:
            return json.loads(response.read())

    def send_queue(self, workflow_json):
        prompt_id = str(uuid.uuid4())

        resp_code, resp_body = self.get_queue_prompt(workflow_json, prompt_id)
        if isinstance(resp_body, str):
            resp_body = json.loads(resp_body)
        if resp_code != 200:
            self.ws.close()
            sys.exit(json.dumps(resp_body, indent=4))

        while True:
            out = self.ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing":
                    data = message["data"]
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break  # Execution is done
            else:
                continue
        print(json.dumps(self.get_history(prompt_id), indent=4))


if True:  # Example
    workflow = {
        "3": {
            "class_type": "KSampler",
            "inputs": {
                "cfg": 8,
                "denoise": 1,
                "latent_image": ["5", 0],
                "model": ["4", 0],
                "negative": ["7", 0],
                "positive": ["6", 0],
                "sampler_name": "euler_ancestral",
                "scheduler": "normal",
                "seed": 8566257,
                "steps": 20,
            },
        },
        "4": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "illustrij_v20.safetensors"},
        },
        "5": {
            "class_type": "EmptyLatentImage",
            "inputs": {"batch_size": 1, "height": 720, "width": 720},
        },
        "6": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": "masterpiece best quality girl"},
        },
        "7": {
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["4", 1], "text": "bad hands, bad pose, bad anatomy"},
        },
        "8": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["3", 0], "vae": ["4", 2]},
        },
        "9": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": "ComfyUI", "images": ["8", 0]},
        },
    }

    # workflow["6"]["inputs"]["text"] = "masterpiece best quality naked woman presenting her genitalia"
    workflow["6"]["inputs"][
        "text"
    ] = "masterpiece best quality girl, fur coat, delicate necklace, thigh-high lace stockings, lace garter belt, garter straps, lace collar, lace bodysuit, open-cup lingerie, tiara, MSFit01 <lora:MSFit01-000001:1>, masterpiece, high_quality, highres, 1woman, adult, ass, black hair, breasts, lips, long hair, looking at viewer, looking back, medium breasts, mole, nipples, shadow,solo, standing, from below, pink labia, one leg up"
    workflow["7"]["inputs"]["text"] = "worst_quality, bad_quality, poorly_detailed,"
    workflow["3"]["inputs"]["seed"] = 21551

    comfy = comfy_ui(ws_timeout=60)
    import random

    for i in range(10):
        workflow["3"]["inputs"]["seed"] = random.randint(1, 10000)
        comfy.socket_connect()
        comfy.send_queue(workflow)
        comfy.socket_close()
"""