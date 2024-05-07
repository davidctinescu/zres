import re

def generate_asm(lines):
    asm_code = """global _start

section .data\n"""

    in_main = False
    variables = {}

    for idx, line in enumerate(lines, start=1):
        if ";" not in line:
            if "{" in line or "}" in line:
                pass
            else:
                raise ValueError(f"Delimiter ';' not found in line {idx}")
        if "//" in line:
            line = line.split("//")[0]
        if "global main" in line:
            in_main = True
            continue
        elif in_main:
            if "}" in line:
                in_main = False
                break
            elif "out" in line:
                if "(" in line and ")" in line:
                    string = re.search(r'out\((.*?)\)', line).group(1)
                    if string.startswith('"') and string.endswith('"'):
                        string = string[1:-1]
                        asm_code += f"msg_{idx} db '{string}', 0xA, 0\n"
                    else:
                        content = variables.get(string, f"var_{len(variables)}")
                        asm_code += f"{content} db '{string}', 0xA, 0\n"
                else:
                    raise ValueError(f"Line {idx} has the wrong format for outputting")
            elif "var" in line:
                var_name = line.split()[1].rstrip(";")
                var_value = re.search(r'("[^"]*"|\d+)', line).group(1)
                variables[var_name] = f"var_{idx}"
            elif "exit" in line:
                exit_code = line.strip().split(" ")[1].rstrip(';')

    asm_code += """section .text

_start:\n"""

    in_main = False

    for idx, line in enumerate(lines, start=1):
        if ";" not in line:
            if "{" in line or "}" in line:
                pass
            else:
                raise ValueError(f"Delimiter ';' not found in line {idx}")
        if "//" in line:
            line = line.split("//")[0]
        if "main {" in line:
            in_main = True
            continue
        elif in_main:
            if "}" in line:
                in_main = False
                break
            elif "out" in line:
                if "(" in line and ")" in line:
                    string = re.search(r'out\((.*?)\)', line).group(1)
                    if string.startswith('"') and string.endswith('"'):
                        string = string[1:-1]
                        asm_code += f"  mov rax, 1\n"
                        asm_code += f"  mov rdi, 1\n"
                        asm_code += f"  mov rsi, msg_{idx}\n"
                        asm_code += f"  mov rdx, {len(string) + 1}\n"
                        asm_code += f"  syscall\n\n"
                    else:
                        content = variables.get(string, f"var_{idx}")
                        asm_code += f"  mov rax, 1\n"
                        asm_code += f"  mov rdi, 1\n"
                        asm_code += f"  mov rsi, {content}\n"
                        asm_code += f"  mov rdx, {len(string) + 1}\n"
                        asm_code += f"  syscall\n\n"
                else:
                    raise ValueError(f"Line {idx} has the wrong format for outputting")

            elif "exit" in line:
                asm_code += f"  mov rax, {exit_code}\n"
                asm_code += f"  mov rdi, rax\n"
                asm_code += f"  mov rax, 60\n"
                asm_code += f"  syscall\n"

    return asm_code
