# -*- coding: utf-8 -*-
import os, csv, os, json, time, pprint, sys, shutil, random, traceback
import system_manager
import production_manager
from notionDatabase import notionDatabase as ntdb

print(__file__)
base_path = os.path.dirname(os.path.abspath(__file__))


class chatgpt:
    def __init__(self):
        self.dc_cfg_path = os.path.join(base_path, "raspi_dcbot.json")
        self.dc_cfg = json.load(open(self.dc_cfg_path))
        #self.dc_cfg["open_ai_gpt"]["model"] = "gpt-3.5-turbo"
        self.dc_cfg["open_ai_gpt"]["model"] = "gpt-4o-mini"
        self.client = system_manager.chatgpt_client(
            model=self.dc_cfg["open_ai_gpt"]["model"],
            api_key=self.dc_cfg["open_ai_gpt"]["api_key"],
        )
        self.system_dict = {
            "general": {
                "role": "system",
                "content": "You are a helpful assistant. you will say straightforward, "
                "avoiding indirect language. "
                "listing out  can be easily to read and understand",
            },
            "" : "",
            # "" : "",
        }

    def chat(self, **kwargs):
        self.client.chat(**kwargs)
        result = self.client.chat(**kwargs)
        return result
