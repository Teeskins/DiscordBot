"""Teeskins requests module"""

import requests

from utils.config import DockerConfig
from typing import Union

config = DockerConfig("config.ini")

class TeeskinsAPI:
    """
        Class used to manage request with the skins.tw API
    """

    HOST = config.get_var("TEESKINS", "HOST")

    def request(_type: callable, *args, **kwargs) -> object:
        """
            Teeskins HTTP request
        """

        try:
            req = _type(*args, **kwargs)

            if req.status_code != 200 or not req.text:
                return None

            return req
        except:
            return None

    def common_request(func: callable, route: str, param: str) -> Union[dict, None]:
        """
            Common Teeskins HTTP request
        """

        req = TeeskinsAPI.request(
            func,
            url=TeeskinsAPI.HOST + route + param
        )

        if not req:
            return None

        return req.json()

    def user_role(token: str) -> Union[dict, None]:
        """
            Gets an user role
        """

        return TeeskinsAPI.common_request(
            requests.get,
            "/api/discord/",
            token
        )

    def asset(_id: str) -> Union[dict, None]:
        """
            Gets asset informations
        """

        return TeeskinsAPI.common_request(
            requests.get,
            "/api/asset/",
            _id
        )

    def random_asset(category: str) -> Union[dict, None]:
        """
            Gets a random asset from the category
        """

        return TeeskinsAPI.common_request(
            requests.get,
            "/api/random/",
            category
        )

    def search(name: str) -> Union[dict, None]:
        """
            Find every asset that contains name in their name
        """

        return TeeskinsAPI.common_request(
            requests.get,
            "/search/",
            name
        )

    def upload_asset(content: bytes, **data) -> bool:
        """
            Upload an asset to skins.tw and put it in the waiting queue
        """

        req = TeeskinsAPI.request(
            requests.post,
            url=TeeskinsAPI.HOST + "/api/storeAsset/discord",
            files={
                "file": content
            },
            data=data,
            headers={ 
                "User-Agent": "Mozilla/5.0",
                "Accept": "application/json"
            }
        )

        if not req:
            return False
        
        return req.json()["success"]

    def duplicate(checksum: str) -> Union[dict, None]:
        """
            Looking for duplicate asset that is already in the database
        """

        return TeeskinsAPI.common_request(
            requests.get,
            "/checkDuplicate/",
            checksum
        )
