import re
# Should create a generic parser for this
def parse_code(output):
    python_code = None
    explain_code = None
    pattern = r"(?P<code>```python(?P<python>.*?)```)?(?P<explanation>.*?)$"
    python_code_match = re.search(pattern, output, re.DOTALL)
    python_code = python_code_match.group("python")
    explain_code = python_code_match.group("explanation")
    return python_code, explain_code

test="""import streamlit
"""

print(parse_code(test))