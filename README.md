# ZRES Compiler

## Description
Simple x86_64 compiler for the ZRES programming language.

## Usage
1. Make sure you have NASM and LD installed if you are using a UNIX based system or NASM for Windows and MinGW if you are using Windows.
2. Run the script with the input file as an argument.

```bash
python compiler.py <input_file>
```

## Syntax
- Delimit lines with `;`.
- The file must have a `global main` declaration to mark the beginning of the main function.
- Use `out("string")` to output strings.
- Use `exit code` to specify the exit code.

Example:
```plaintext
global main {
    out("Hello, world!");
    exit(0);
}
```

## Author
windowsbuild3r
