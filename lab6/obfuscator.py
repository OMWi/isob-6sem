import code
import re
import string
import time
import random

not_vars = [
    "__init__"
]

def random_name():
    return (
            random.choice(string.ascii_letters)
            + random.choice(string.ascii_letters)
            + str(time.time()).replace(".", "")
        )


def obfuscate(code_str):
    code_str = "\n" + code_str
    start = 0
    # "".find()
    fun_names = []
    while True:
        name = code_str.find("def ", start)
        bracket = code_str.find("(", name)
        fun_name = code_str[name+4:bracket]
        start = bracket
        if fun_name in not_vars:
            continue
        fun_names.append(fun_name)
        # code_str = code_str.replace(f"{fun_name}(", f"{random_name}(")
        # fun_names.append(fun_name)
        if start == -1:
            break
    for fun_name in fun_names:
        if fun_name in not_vars:
            continue
        code_str = code_str.replace(f"{fun_name}(", f"{random_name()}(")



    # variable_names = re.findall(r"def (\w+)(", code_str)
    # for variable_name in variable_names:
    #     if variable_name in not_vars:
    #         continue
    #     code_str = code_str.replace(f" {variable_name[0]} ", f" {random_name()} ")
    return code_str

if __name__ == "__main__":
    file_name = "code.py"
    code_str = ""
    with open(file_name, "r") as f:
        code_str = f.read()
    res = obfuscate(code_str)
    with open("ob_res.py", "w") as f:
        f.write(res)
