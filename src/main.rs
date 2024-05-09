use std::env;
use std::process;

pub mod compilefiles;

// use crate::libs::compilefiles::compile_file;

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() != 2 {
        eprintln!("Usage: {} <input_file>", args[0]);
        process::exit(1);
    }

    let input_file = &args[1];

    match compilefiles::compile_file(input_file) {
        Ok(exe_file) => {
            println!("Compilation successful. Executable file: {}", exe_file);
        }
        Err(e) => {
            eprintln!("Error: {}", e);
            process::exit(1);
        }
    }
}
