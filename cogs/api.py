#!/usr/bin/env python3

import json, requests
from typing import *
from configparser import ConfigParser

config: ConfigParser = ConfigParser()
config.read("config.ini")

class ApiInfos:
    url = config.get("API", "TW_UTILS")

class Api(ApiInfos):
    """Manage API requests"""

    def get(self, route: str, data: json):
        req = {
            "url": self.url + route,
            "json": data
        }
        res = requests.get(**req)
        return (res)
    
    def render(self, data: json):
        return (self.get("/render", data))
    
    def renderColor(self, data: json):
        return (self.get("/renderColor", data))

    def changer(self, data: json):
        return (self.get("/changer", data))
