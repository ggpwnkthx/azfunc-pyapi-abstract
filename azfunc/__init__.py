from libs.utils.pluginloader import load
from pathlib import Path
__bootstrap__ = str(Path(Path(__file__).parent, "bootstrap"))
__endpoints__ = str(Path(Path(__file__).parent, "endpoints"))

# Bootstrap
load(__bootstrap__, file_mode="all", depth=-1)

# Create App Instance
import libs.azure.functions as func

app = func.FunctionApp()

# Initialize Endpoints
load(__endpoints__, file_mode="all", depth=-1)
