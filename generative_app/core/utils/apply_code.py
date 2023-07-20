""" stores the functions to apply the generated code on the app """

import re
from utils.parser import parse_generated_code
from templates.template_app import template_app


def apply_code_on_gen_app(prev_app, curr_app, username, script_path, code_generated):
    if curr_app == f"{username} - Generated App":
        apply_code_if_exist(script_path, code_generated)


def apply_code_if_exist(script_path, code_generated):
    #  Current code
    with open(script_path, "r") as app_file:
        current_code = parse_generated_code(app_file.read())

    if code_generated is not None:
        print("current_code ", current_code)
        print("code_generated ", code_generated)
        if current_code != code_generated:
            print("Applying generated code")
            with open(script_path, "w") as app_file:
                code_generated = re.sub(
                    r"^", " " * 8, code_generated, flags=re.MULTILINE
                )
                app_file.write(template_app.format(code=code_generated))
