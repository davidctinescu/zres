import subprocess
import os
from generateassembly import generate_asm

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
    subprocess.run(['ld', obj_file, '-o', f"{exe_file}"], check=True)

    # os.remove(asm_file)
    os.remove(obj_file)

    return exe_file