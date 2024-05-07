import re

def generate_asm(lines):
    asm_code = """global _start

section .data\n"""

    in_main = False
    variables = {}

    for idx, line in enumerate(lines, start=1):
        if "{" in line or "}" in line:
            continue
        if ";" not in line:
            raise ValueError(f"Delimiter ';' not found in line {idx}")
        parts = line.split(";")
        for part in parts:
            if "//" in part:
                continue
            if "global main" in part:
                in_main = True
                continue
            elif in_main:
                if "}" in part:
                    in_main = False
                    break
                elif "out" in part:
                    if "(" in part and ")" in part:
                        string = part.strip().split("(", 1)[1].split(")", 1)[0]
                        if string.startswith('"') and string.endswith('"'):
                            string = string[1:-1]
                            asm_code += f"msg_{idx} db '{string}', 0xA, 0\n"
                        else:
                            content = part[part.find("(") + 1:part.find(")")]
                            if content in variables:
                                content = variables[content]
                            else:
                                content = f"var_{len(variables)}"
                            asm_code += f"var_{idx} db '{content}', 0xA, 0\n"
                    else:
                        raise ValueError(f"Line {idx} has the wrong format for outputting")
                elif "var" in part:
                    var_name = part.split()[1].rstrip(";")
                    var_value = re.search(r'("[^"]*"|\d+)', part).group(1)
                    variables[var_name] = var_value
                elif "exit" in part:
                    exit_code = part.strip().split(" ")[1].rstrip(';')

    asm_code += """section .text

_start:\n"""

    in_main = False

    for idx, line in enumerate(lines, start=1):
        if "{" in line or "}" in line:
            continue
        if ";" not in line:
            raise ValueError(f"Delimiter ';' not found in line {idx}")
        parts = line.split(";")
        for part in parts:
            if "//" in part:
                continue
            if "main {" in part:
                in_main = True
                continue
            elif in_main:
                if "}" in part:
                    in_main = False
                    break
                elif "out" in part:
                    if "(" in part and ")" in part:
                        string = part.strip().split("(", 1)[1].split(")", 1)[0]
                        if string.startswith('"') and string.endswith('"'):
                            string = string[1:-1]
                            asm_code += f"  mov rax, 1\n"
                            asm_code += f"  mov rdi, 1\n"
                            asm_code += f"  mov rsi, msg_{idx}\n"
                            asm_code += f"  mov rdx, {len(string) + 1}\n"
                            asm_code += f"  syscall\n\n"
                        else:
                            content = part[part.find("(") + 1:part.find(")")]
                            if content in variables:
                                content = variables[content]
                                asm_code += f"  mov rax, 1\n"
                                asm_code += f"  mov rdi, 1\n"
                                asm_code += f"  mov rsi, var_{idx}\n"
                                asm_code += f"  mov rdx, {len(content) + 1}\n"
                                asm_code += f"  syscall\n\n"
                    else:
                        raise ValueError(f"Line {idx} has the wrong format for outputting")

                elif "exit" in part:
                    asm_code += f"  mov rax, {exit_code}\n"
                    asm_code += f"  mov rdi, rax\n"
                    asm_code += f"  mov rax, 60\n"
                    asm_code += f"  syscall\n"

    return asm_code