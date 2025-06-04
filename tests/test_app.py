from gradio_client import Client

client = Client("http://127.0.0.1:7860/")

# Test case for Code Analysis Report
code_for_analysis = "print('Hello, world!')"
result_report = client.predict(code=code_for_analysis, api_name="/predict")
print("Code Analysis Report result:", result_report)
assert (
    isinstance(result_report, str)
    and "Analysis Report for provided code:" in result_report
)

# Test case for Code Score
code_for_score = "def my_function():\n  pass"
result_score = client.predict(code=code_for_score, api_name="/predict_1")
print("Code Score result:", result_score)
assert isinstance(result_score, str) and "Code Score for provided code:" in result_score
