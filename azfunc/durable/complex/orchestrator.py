from ... import app

# Orchestrator
@app.orchestration_trigger(context_name="context")
def complex_root(context):
    result1 = yield context.call_activity("complex_hello", "Seattle")
    result2 = yield context.call_activity("complex_hello", "Tokyo")
    result3 = yield context.call_activity("complex_hello", "London")

    return [result1, result2, result3]