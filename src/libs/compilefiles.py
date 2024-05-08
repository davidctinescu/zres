import subprocess
import os
import platform
from .assembly import generate_assembly, tokenizer_ir

def compile_file(input_file):
    output_file = os.path.splitext(input_file)[0]
    asm_file = output_file + '.asm'
    obj_file = output_file + '.o'
    if platform.system() == "Windows":
        exe_file = output_file + '.exe'
    else:
        exe_file = output_file + '.out'
    
    with open(input_file, 'r') as f:
        lines = f.readlines()

    _, entry_point, _ = tokenizer_ir(lines)

    asm_code = generate_assembly(lines, entry_point)
    
    with open(asm_file, 'w') as f:
        f.write(asm_code)

    if platform.system() == "Windows":
        subprocess.run(['nasm', '-f', 'win64', asm_file, '-o', obj_file], check=True)
        subprocess.run(['gcc','-e', entry_point, obj_file, '-o', exe_file, '-nostartfiles', '-nostdlib', '-lkernel32'], check=True)
    else:
        subprocess.run(['nasm', '-f', 'elf64', asm_file, '-o', obj_file], check=True)
        subprocess.run(['ld','-e', entry_point, obj_file, '-o', exe_file], check=True)

    os.remove(asm_file)
    os.remove(obj_file)

    return exe_file