# ZRES Compiler

## Description
Simple x86_64 compiler for the ZRES programming language.

## Usage
1. Make sure you have NASM and LD installed if you are using a UNIX based system.
2. Run the script with the input file as an argument.

```bash
python main.py <input_file>
```

Example:
```plaintext
global main {
    out("Hello, world!");
    exit(0);
}
```
Where `global funcname` is the entry point.

## Windows support:
- Currently windows is not supported, letting this be a UNIX only programming language (for now)
- Why? I cant print to stdout, if anyone knows a fix, please let me know!

## Author
windowsbuild3r
