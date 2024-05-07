import re
import os

def generate_asm_linux(lines) -> str:
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
                    output_content = re.search(r'out\((.*?)\)', line).group(1).strip()
                    if output_content.startswith('"') and output_content.endswith('"'):
                        string = output_content[1:-1]
                        variables[f"msg_{idx}"] = string
                        asm_code += f"msg_{idx} db '{string}', 0xA, 0\n"
                    else:
                        if output_content in variables:
                            pass
                        else:
                            raise ValueError(f"Variable '{output_content}' not declared")
                else:
                    raise ValueError(f"Line {idx} has the wrong format for outputting")
            elif "var" in line:
                var_name = line.split()[1].rstrip(";")
                var_value = re.search(r'("[^"]*"|\d+)', line).group(1)
                if var_value.startswith('"') and var_value.endswith('"'):
                    var_value = var_value[1:-1]
                if var_name not in variables:
                    variables[var_name] = var_value
                    asm_code += f"{var_name} db '{var_value}', 0xA, 0\n"
                else:
                    raise ValueError(f"Variable '{var_name}' already declared")
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
                        content = variables.get(string)
                        if content is None:
                            raise ValueError(f"Variable '{string}' not declared")
                        asm_code += f"  mov rax, 1\n"
                        asm_code += f"  mov rdi, 1\n"
                        asm_code += f"  mov rsi, {var_name}\n"
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

def generate_asm_windows(lines) -> str:
    asm_code = """section .data:
"""

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
                    output_content = re.search(r'out\((.*?)\)', line).group(1).strip()
                    if output_content.startswith('"') and output_content.endswith('"'):
                        string = output_content[1:-1]
                        variables[f"msg_{idx}"] = string
                        asm_code += f"  msg_{idx} db '{string}', 0xA, 0\n"
                    else:
                        if output_content in variables:
                            pass
                        else:
                            raise ValueError(f"Variable '{output_content}' not declared")
                else:
                    raise ValueError(f"Line {idx} has the wrong format for outputting")
            elif "var" in line:
                var_name = line.split()[1].rstrip(";")
                var_value = re.search(r'("[^"]*"|\d+)', line).group(1)
                if var_value.startswith('"') and var_value.endswith('"'):
                    var_value = var_value[1:-1]
                if var_name not in variables:
                    variables[var_name] = var_value
                    asm_code += f"  {var_name} db '{var_value}', 0xA, 0\n"
                else:
                    raise ValueError(f"Variable '{var_name}' already declared")
            elif "exit" in line:
                exit_code = line.strip().split(" ")[1].rstrip(';')

    asm_code += """
section .text:
    extern ExitProcess: proc
    extern GetStdHandle: proc
    extern WriteConsoleA: proc

global main

main:
"""

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
                        asm_code += f"  mov rdx, {len(string)}\n"
                        asm_code += f"  lea rcx, [msg_{idx} + rip]\n"
                        asm_code += f"  call WriteConsoleA\n\n"
                    else:
                        content = variables.get(string)
                        if content is None:
                            raise ValueError(f"Variable '{string}' not declared")
                        asm_code += f"  mov rdx, {len(content)}\n"
                        asm_code += f"  lea rcx, [{string} + rip]\n"
                        asm_code += f"  call WriteConsoleA\n\n"
                else:
                    raise ValueError(f"Line {idx} has the wrong format for outputting")

            elif "exit" in line:
                asm_code += f"  mov ecx, {exit_code}\n"
                asm_code += f"  call ExitProcess\n"

    return asm_code



def generate_asm(lines) -> str:
    asm_code = ""
    if os.name == 'nt':
        asm_code = generate_asm_windows(lines)
    else:
        asm_code = generate_asm_linux(lines)

    return asm_code