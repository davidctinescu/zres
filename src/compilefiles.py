import subprocess
import os
from generateassembly import generate_asm

def compile_file(input_file):
    output_file = os.path.splitext(input_file)[0]
    asm_file = output_file + '.asm'
    obj_file = output_file + '.o'
    if os.name == 'nt':
        exe_file = output_file + '.exe'
    else:
        exe_file = output_file + '.out'
    
    with open(input_file, 'r') as f:
        lines = f.readlines()

    asm_code = generate_asm(lines)
    
    with open(asm_file, 'w') as f:
        f.write(asm_code)

    if os.name == 'nt':
        subprocess.run(['nasm.exe', '-f', 'win64', asm_file, '-o', obj_file], check=True)
        subprocess.run(['gcc.exe', obj_file, '-o', exe_file, '-lkernel32'], check=True)
    else:
        subprocess.run(['nasm', '-f', 'elf64', asm_file, '-o', obj_file], check=True)
        subprocess.run(['ld', obj_file, '-o', exe_file], check=True)

    os.remove(asm_file)
    os.remove(obj_file)

    return exe_file