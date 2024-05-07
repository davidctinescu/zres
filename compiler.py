import subprocess
import sys
import os

RED = "\033[91m"
RESET = "\033[0m"

def generate_asm(lines):
    asm_code = """global _start

section .data\n"""

    in_main = False

    for idx, line in enumerate(lines, start=1):
        if "//" in line:
            continue
        if "global main {" in line:
            in_main = True
            continue
        elif in_main:
            if "}" in line:
                in_main = False
                break
            elif "out" in line:
                string = line.strip().split("(", 1)[1].split(")", 1)[0]
                if string.startswith('"') and string.endswith('"'):
                    string = string[1:-1]
                    asm_code += f"msg_{idx} db '{string}', 0xA, 0\n"
            elif "exit" in line:
                exit_code = line.strip().split(" ")[1].rstrip(';')
                asm_code += f"exit_code db '{exit_code}'\n"
    
    asm_code += """section .text

_start:\n"""

    in_main = False

    for idx, line in enumerate(lines, start=1):
        if "//" in line:
            continue
        if "global main {" in line:
            in_main = True
            continue
        elif in_main:
            if "}" in line:
                in_main = False
                break
            elif "out" in line:
                string = line.strip().split("(", 1)[1].split(")", 1)[0]
                if string.startswith('"') and string.endswith('"'):
                    string = string[1:-1]
                    asm_code += f"  mov rax, 1\n"
                    asm_code += f"  mov rdi, 1\n"
                    asm_code += f"  mov rsi, msg_{idx}\n"
                    asm_code += f"  mov rdx, {len(string) + 1}\n"
                    asm_code += f"  syscall\n\n"
            elif "exit" in line:
                asm_code += f"  mov rax, {exit_code}\n"
                asm_code += f"  mov rdi, rax\n"
                asm_code += f"  mov rax, 60\n"
                asm_code += f"  syscall\n"
    
    return asm_code

def compile_file(input_file):
    output_file = os.path.splitext(input_file)[0]
    asm_file = output_file + '.asm'
    obj_file = output_file + '.o'
    exe_file = output_file + '.out'
    
    with open(input_file, 'r') as f:
        lines = f.readlines()

    asm_code = generate_asm(lines)
    
    with open(asm_file, 'w') as f:
        f.write(asm_code)
    
    subprocess.run(['nasm', '-f', 'elf64', asm_file, '-o', obj_file], check=True)
    
    subprocess.run(['ld', obj_file, '-o', exe_file], check=True)

    os.remove(asm_file)
    os.remove(obj_file)

    return exe_file

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <input_file>")
        return
    
    input_file = sys.argv[1]
    try:
        exe_file = compile_file(input_file)
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

if __name__ == "__main__":
    main()
