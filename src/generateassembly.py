import re

def generate_asm(lines):
    asm_code = """global _start

section .data\n"""

    in_main = False
    variables = {}

    for idx, line in enumerate(lines, start=1):
        if "//" in line:
            continue
        if "global main" in line:
            in_main = True
            continue
        elif in_main:
            if "}" in line:
                in_main = False
                break
            elif "out" in line:
                if "(" in line and ")" in line:
                    string = line.strip().split("(", 1)[1].split(")", 1)[0]
                    if string.startswith('"') and string.endswith('"'):
                        string = string[1:-1]
                        asm_code += f"msg_{idx} db '{string}', 0xA, 0\n"
                    else:
                        content = line[line.find("(") + 1:line.find(")")]
                        if content in variables:
                            content = variables[content]
                        else:
                            content = f"var_{len(variables)}"
                        asm_code += f"var_{idx} db '{content}', 0xA, 0\n"
                else:
                    raise ValueError(f"Line {idx} has the wrong format for outputting")
            elif "var" in line:
                var_name = line.split()[1].rstrip(";")
                var_value = re.search(r'("[^"]*"|\d+)', line).group(1)
                variables[var_name] = var_value
            elif "exit" in line:
                exit_code = line.strip().split(" ")[1].rstrip(';')

    asm_code += """section .text

_start:\n"""

    in_main = False

    for idx, line in enumerate(lines, start=1):
        if "//" in line:
            continue
        if "main {" in line:
            in_main = True
            continue
        elif in_main:
            if "}" in line:
                in_main = False
                break
            elif "out" in line:
                if "(" in line and ")" in line:
                    string = line.strip().split("(", 1)[1].split(")", 1)[0]
                    if string.startswith('"') and string.endswith('"'):
                        string = string[1:-1]
                        asm_code += f"  mov rax, 1\n"
                        asm_code += f"  mov rdi, 1\n"
                        asm_code += f"  mov rsi, msg_{idx}\n"
                        asm_code += f"  mov rdx, {len(string) + 1}\n"
                        asm_code += f"  syscall\n\n"
                    else:
                        content = line[line.find("(") + 1:line.find(")")]
                        if content in variables:
                            content = variables[content]
                            asm_code += f"  mov rax, 1\n"
                            asm_code += f"  mov rdi, 1\n"
                            asm_code += f"  mov rsi, var_{idx}\n"
                            asm_code += f"  mov rdx, {len(content) + 1}\n"
                            asm_code += f"  syscall\n\n"
                else:
                    raise ValueError(f"Line {idx} has the wrong format for outputting")

            elif "exit" in line:
                asm_code += f"  mov rax, {exit_code}\n"
                asm_code += f"  mov rdi, rax\n"
                asm_code += f"  mov rax, 60\n"
                asm_code += f"  syscall\n"

    return asm_code
