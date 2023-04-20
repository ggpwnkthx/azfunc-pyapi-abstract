from libs.utils.pluginloader import load
from pathlib import Path
__parent__ = str(Path(__file__).parent)
__bootstrap__ = str(Path(__parent__, "bootstrap"))
__durable__ = str(Path(__parent__, "durable"))
__endpoints__ = str(Path(__parent__, "endpoints"))

# Bootstrap
load(__bootstrap__, file_mode="all", depth=2)

# Create App Instance
from libs.azure.functions import FunctionApp, AuthLevel

app = FunctionApp(http_auth_level=AuthLevel.FUNCTION)

# Initialize Endpoints
load(__durable__, file_mode="all", depth=2)
load(__endpoints__, file_mode="all", depth=2)
