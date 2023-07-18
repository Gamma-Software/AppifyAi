import re

def analyze_security(code):
    """ Analyze the code for security issues
        Return True if the code is not safe
    """
    # For now we only check if the code contains the word "exec" and "os.system"
    if code is None:
        raise ValueError("Code cannot be parsed")
    exploit = ["subprocess.run", "exec", "os.system", "subprocess.Popen", "os.exec*", "os.execvp", "eval"]
    # Check regex for exploit
    for exp in exploit:
        if re.search(exp, code):
            return True
    return False