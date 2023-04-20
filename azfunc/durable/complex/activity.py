from ... import app

# Activity
@app.activity_trigger(input_name="city")
def complex_hello(city: str):
    return "Hello " + city
