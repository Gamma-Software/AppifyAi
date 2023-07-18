import re

def parse_current_app(code:str):
    from textwrap import dedent
    python_code = None
    pattern = r"#---start\n(.*?)#---end"
    python_code_match = re.search(pattern, code, re.DOTALL)
    if python_code_match:
        python_code = python_code_match.group(1)
        if python_code == "None":
            python_code = None
    # Remove the 8 space indentation
    if python_code:
        python_code = dedent(python_code)
    return python_code