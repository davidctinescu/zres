# ZRES Compiler

## Description
Simple x86_64 compiler for the ZRES programming language.

## Usage
1. Make sure you have NASM and GNU (maybe MUSL) installed if you are using Linux. For windows, make sure you have MinGW and NASM for windows
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
- Currently windows is not supported, letting this be a Linux only programming language (for now)
- Why? I cant print to stdout, if anyone knows a fix, please let me know!
- Also why not OSX? I don't have access to a mac nor do i plan on buying one.

## Author
windowsbuild3r
