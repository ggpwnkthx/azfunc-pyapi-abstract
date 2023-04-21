from .__singletons__ import Galactus, auth_cache
from datetime import datetime
from typing import Union
import azure.functions as func
import requests


def MicrosoftGraph(request: func.HttpRequest, token, auth):
    if (
        (
            not request.headers.get("X-Forwarded-For")
            or request.headers.get("X-Forwarded-For").split(":")[0].strip()
            == auth["ipaddr"]
        )
        and datetime.now() < datetime.fromtimestamp(auth["exp"])
        and "MicrosoftGraph" in auth_cache.keys()
        and auth["appid"] in auth_cache["MicrosoftGraph"].keys()
        and auth["oid"] in auth_cache["MicrosoftGraph"][auth["appid"]].keys()
        and auth["ipaddr"]
        in auth_cache["MicrosoftGraph"][auth["appid"]][auth["oid"]].keys()
        and "error"
        not in auth_cache["MicrosoftGraph"][auth["appid"]][auth["oid"]][
            auth["ipaddr"]
        ].keys()
    ):
        return auth_cache["MicrosoftGraph"][auth["appid"]][auth["oid"]][auth["ipaddr"]]

    r = requests.post(
        "https://graph.microsoft.com/beta/$batch",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "requests": [
                {"url": "/me", "method": "GET", "id": "1"},
                {
                    "url": "/me/transitiveMemberOf/microsoft.graph.group",
                    "method": "GET",
                    "id": "2",
                },
            ]
        },
    ).json()

    if "responses" in r.keys():
        subject: Union[dict, None] = next(
            (x["body"] for x in r["responses"] if x["id"] == "1"), None
        )
        if subject:
            subject["groups"] = next(
                (x["body"]["value"] for x in r["responses"] if x["id"] == "2"), None
            )
            if subject["groups"]:
                subject["groups"] = list(map(lambda x: x["id"], subject["groups"]))
    else:
        subject = r

    if "error" not in subject.keys():
        if "MicrosoftGraph" not in auth_cache.keys():
            auth_cache["MicrosoftGraph"] = {}
        if auth["appid"] not in auth_cache["MicrosoftGraph"].keys():
            auth_cache["MicrosoftGraph"][auth["appid"]] = {}
        if auth["oid"] not in auth_cache["MicrosoftGraph"][auth["appid"]].keys():
            auth_cache["MicrosoftGraph"][auth["appid"]][auth["oid"]] = {}
        auth_cache["MicrosoftGraph"][auth["appid"]][auth["oid"]][
            auth["ipaddr"]
        ] = subject

    return subject


Galactus["sts.windows.net"] = MicrosoftGraph
Galactus["login.microsoftonline.com"] = MicrosoftGraph
