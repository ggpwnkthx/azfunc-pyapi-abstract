# from py_abac.storage.sql import SQLStorage
from .azure.table.storage import AzureTableStorage
from py_abac import PDP, Policy, AccessRequest
from functools import wraps
from libs.utils.threaded import current
import os


class AuthorizationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Authorization:
    def __init__(self):
        self.storage = AzureTableStorage(
            table_name=str(
                os.environ.get("flask_abac_table")
                if os.environ.get("flask_abac_table")
                else "pyabac"
            ),
            conn_str=os.environ["AzureWebJobsStorage"],
        )

    def is_allowed(self, subject=None, resource=None, action=None, context=None):
        if not subject and current.subject:
            subject = current.subject
        if not resource and current.resource:
            resource = current.resource
        if not action and current.action:
            action = current.action
        if not context and current.context:
            context = current.context
        else:
            context = {}
        return PDP(self.storage).is_allowed(
            AccessRequest.from_json(
                {
                    "subject": {"id": "", "attributes": subject},
                    "resource": {"id": "", "attributes": resource},
                    "action": {"id": "", "attributes": action},
                    "context": context,
                }
            )
        )

    def check(self, resource=None, action=None, context={}):
        if not resource and current.request:
            resource = {
                key: value for key, value in current.request.route_params.items()
            }
        if not action and current.request:
            action = {"method": current.request.method}
        if not self.is_allowed(resource, action, context):
            raise AuthorizationException(
                {
                    "code": "InvalidPermission",
                    "message": "Requesting subject does not have permission to access the requested resource or does not have permission to perform the requested action.",
                }
            )

    def can(self, resource, action, context={}):
        def wrapper(function):
            @wraps(function)
            def inner(*args, **kwargs):
                self.check(resource, action, context)
                return function(
                    *args,
                    **kwargs,
                )

            return inner

        return wrapper

    gatekeeper = can

    def add_policy(
        self,
        name: str,
        rules: dict,
        description: str = "",
        effect: str = "allow",
        targets: dict = {},
        priority: int = 0,
    ):
        policy = Policy.from_json(
            {
                "uid": name,
                "description": description,
                "effect": effect,
                "rules": rules,
                "targets": targets,
                "priority": priority,
            }
        )
        self.storage.add(policy)

    def delete_policy(self, name: str):
        self.storage.delete(name)
