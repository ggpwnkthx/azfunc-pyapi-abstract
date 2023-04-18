# Bootstrap Stuff Goes Here
from . import bindings


# Create App Instance
import libs.azure.functions as func

app = func.FunctionApp()

# Initialize Extensions
from . import endpoints