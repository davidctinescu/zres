import re
import os

def tokenizer_ir(lines):
    ir_code = []
    variables = {}
    entry_point = None

    for idx, line in enumerate(lines, start=1):
        # Check for delimiter
        if ";" not in line:
            # Check for function
            if "{" in line or "}" in line:
                pass
            else:
                # Error: no operand
                raise ValueError(f"Cannot resolve operand at line {idx}")

        # Parse comments
        line = line.split("//")[0]

        # Check for main function
        if "global" in line:
            entry_point = line.split()[1].rstrip("{")
            continue  # Continue parsing after main function

        # Check for variables
        if "let" in line:
            var_name = line.split()[1].rstrip(";")
            var_value = re.search(r'("[^"]*"|\d+)', line).group(1)
            # Variable is a string
            if var_value.startswith('"') and var_value.endswith('"'):
                var_value = var_value[1:-1]
            variables[var_name] = var_value
            ir_code.append(("var", var_name, var_value))

        # Check for outputting to std
        elif "out" in line:
            output_content = re.search(r'out\((.*?)\)', line).group(1).strip()
            if output_content.startswith('"') and output_content.endswith('"'):
                string = output_content[1:-1]
                ir_code.append(("out_string", string))
            elif output_content.isdigit():
                ir_code.append(("out_int", output_content))
            else:
                if output_content not in variables:
                    raise ValueError(f"Variable '{output_content}' not declared")
                ir_code.append(("out_var", output_content))

        elif "exit" in line:
            exit_code = re.search(r'exit\((.*?)\)', line).group(1).strip()
            ir_code.append(("exit", exit_code))

    if entry_point is None:
        raise ValueError("Entry point not found!")
    
    return ir_code, entry_point, variables

def generate_assembly_amd64_linux(ir_code, entry_point, variables):
    asm_code = """section .data\n"""

    data_idx = 0

    for instruction in ir_code:
        if instruction[0] == "var":
            var_name, var_value = instruction[1:]
            asm_code += f"  {var_name} db '{var_value}', 0xA, 0\n\n"
            data_idx += 1
        if instruction[0] == "out_string":
            string = instruction[1]
            asm_code += f"  msg_{data_idx} db '{string}', 0xA, 0\n\n"
            data_idx += 1

    asm_code += """section .text\n"""
    asm_code += f"""  global {entry_point}\n\n"""

    asm_code += f"{entry_point}:\n"

    for instruction in ir_code:
        if instruction[0] == "out_string":
            string = instruction[1]
            asm_code += f"  mov rax, 1\n"
            asm_code += f"  mov rdi, 1\n"
            asm_code += f"  lea rsi, [rel msg_{data_idx -1}]\n" 
            asm_code += f"  mov rdx, {len(string) + 1}\n"
            asm_code += f"  syscall\n\n"
        elif instruction[0] == "out_int":
            int_value = instruction[1]
            asm_code += f"  mov rax, 1\n"
            asm_code += f"  mov rdi, 1\n"
            asm_code += f"  mov rsi, {int_value}\n"
            asm_code += f"  mov rdx, 10\n"
            asm_code += f"  syscall\n\n"
        elif instruction[0] == "out_var":
            var_name = instruction[1]
            content = variables.get(var_name)
            if content is None:
                raise ValueError(f"Variable '{var_name}' not declared")
            asm_code += f"  mov rax, 1\n"
            asm_code += f"  mov rdi, 1\n"
            asm_code += f"  mov rsi, {var_name}\n"
            asm_code += f"  mov rdx, {len(content) + 1}\n"
            asm_code += f"  syscall\n\n"
        elif instruction[0] == "exit":
            exit_code = instruction[1]
            asm_code += f"  mov rax, {exit_code}\n"
            asm_code += f"  mov rdi, rax\n"
            asm_code += f"  mov rax, 60\n"
            asm_code += f"  syscall\n"

    return asm_code

def generate_assembly(lines, entry_point) -> str:
    asm_code = None
    ir_code, _, variables = tokenizer_ir(lines)
    asm_code = generate_assembly_amd64_linux(ir_code, entry_point, variables)
    return asm_code