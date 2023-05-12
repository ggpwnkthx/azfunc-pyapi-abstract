from azure.durable_functions import DurableOrchestrationContext
from libs.azure.functions import Blueprint

bp = Blueprint()


# Orchestrator
@bp.orchestration_trigger(context_name="context")
def async_task_handler(context: DurableOrchestrationContext):
    context.set_custom_status("Validating Request Data")
    request = yield context.call_activity("validate_request", context.get_input())

    context.set_custom_status("Awaiting Approval")
    approval = yield context.wait_for_external_event("Approval")
    if approval:
        return "Approved"
    else:
        return "Rejected"
