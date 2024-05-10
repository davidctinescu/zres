use std::fs;
// use std::io;
use std::path::Path;
use std::process::{Command, Stdio};

pub mod assembly;

pub fn compile_file(input_file: &str) -> Result<String, String> {
    let output_file = Path::new(input_file).file_stem().unwrap().to_string_lossy();
    let asm_file = format!("./out/{}.asm", output_file);
    let obj_file = format!("./out/{}.o", output_file);
    let exe_file = if cfg!(windows) {
        format!("./out/{}.exe", output_file)
    } else {
        format!("./out/{}.out", output_file)
    };

    let input_content = fs::read_to_string(input_file).map_err(|e| format!("{}", e))?;
    let lines: Vec<&str> = input_content.lines().collect();

    let (_, entry_point, _, _) = assembly::tokenizer_ir(&lines);

    let asm_code = assembly::generate_assembly(&lines, &entry_point);

    fs::write(&asm_file, asm_code).map_err(|e| format!("{}", e))?;

    let _nasm_cmd = if cfg!(windows) {
        "nasm -f win64"
    } else {
        "nasm -f elf64"
    };
    let _ld_cmd = if cfg!(windows) { "ld -e" } else { "ld -e" };

    let nasm_output = Command::new("nasm")
        .arg("-f")
        .arg(if cfg!(windows) { "win64" } else { "elf64" })
        .arg(&asm_file)
        .arg("-o")
        .arg(&obj_file)
        .stdout(Stdio::null())
        .stderr(Stdio::inherit())
        .status();

    if let Err(err) = nasm_output {
        fs::remove_file(&obj_file).ok();
        println!("Could not assemble!");
        return Err(format!("{}", err));
    }

    let ld_output = Command::new("ld")
        .arg("-e")
        .arg(&entry_point)
        .arg(&obj_file)
        .arg("-o")
        .arg(&exe_file)
        .stdout(Stdio::null())
        .stderr(Stdio::inherit())
        .status();

    if let Err(err) = ld_output {
        fs::remove_file(&obj_file).ok();
        fs::remove_file(&exe_file).ok();
        println!("Could not link!");
        return Err(format!("{}", err));
    }

    fs::remove_file(&asm_file).ok();
    fs::remove_file(&obj_file).ok();

    Ok(exe_file)
}
