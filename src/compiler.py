import sys

from compilefiles import compile_file

def main():
    if len(sys.argv) != 2:
        print("Usage: python compiler.py <input_file>")
        return
    
    input_file = sys.argv[1]
    try:
        exe_file = compile_file(input_file)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
