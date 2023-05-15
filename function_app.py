from azure.functions import AuthLevel
from libs.azure.functions import FunctionApp

app = FunctionApp(http_auth_level=AuthLevel.ANONYMOUS)
app.register_blueprints(
    [
        "libs/azure/functions/blueprints/jsonapi",
        "libs/azure/functions/blueprints/whoami",
        "libs/azure/functions/blueprints/keep_alive"
    ]
)
