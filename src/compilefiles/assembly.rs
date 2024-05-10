use std::collections::HashMap;

pub fn tokenizer_ir(
    lines: &[&str],
) -> (
    Vec<(String, String, String)>,
    String,
    HashMap<String, String>,
    HashMap<String, usize>,
) {
    let mut ir_code = Vec::new();
    let mut variables = HashMap::new();
    let mut entry_point = String::new();
    let mut functions = HashMap::new(); // New HashMap to store function names and their corresponding lines

    for (idx, line) in lines.iter().enumerate().map(|(idx, &line)| (idx + 1, line)) {
        if line.trim().is_empty() {
            continue;
        }

        if line.trim().starts_with("//") {
            continue;
        }

        let line = if let Some(pos) = line.find("//") {
            &line[..pos]
        } else {
            line
        };

        if !line.contains(';') {
            if line.contains('{') || line.contains('}') {
                if line.contains("global") {
                    entry_point = line
                        .split_whitespace()
                        .nth(1)
                        .unwrap()
                        .trim_end_matches('{')
                        .to_string();
                    continue;
                }
                if line.contains("function") {
                    let function_name = line
                        .split_whitespace()
                        .nth(1)
                        .unwrap()
                        .trim_end_matches('{')
                        .to_string();
                    functions.insert(function_name.clone(), idx);
                    continue;
                }
                continue;
            } else {
                panic!("{}", format!("Cannot resolve operand at line {}", idx));
            }
        }

        if line.contains("let") {
            let var_name = line
                .split_whitespace()
                .nth(1)
                .unwrap()
                .trim_end_matches(';')
                .to_string();
            let var_value = regex::Regex::new(r#"("[^"]*"|\d+)"#)
                .unwrap()
                .find(&line)
                .unwrap()
                .as_str()
                .to_string();
            if var_value.starts_with('"') && var_value.ends_with('"') {
                let var_value = var_value.trim_matches('"').to_string();
                variables.insert(var_name.clone(), var_value.clone());
                ir_code.push(("var".to_string(), var_name.clone(), var_value));
            } else {
                variables.insert(var_name.clone(), var_value.clone());
                ir_code.push(("var".to_string(), var_name.clone(), var_value));
            }
        } else if line.contains("out") {
            let output_content = regex::Regex::new(r#"out\((.*?)\)"#)
                .unwrap()
                .captures(&line)
                .unwrap()[1]
                .trim()
                .to_string();
            if output_content.starts_with('"') && output_content.ends_with('"') {
                let string = output_content.trim_matches('"').to_string();
                ir_code.push(("out_string".to_string(), string.clone(), "".to_string()));
            } else if output_content.parse::<i64>().is_ok() {
                ir_code.push((
                    "out_int".to_string(),
                    output_content.clone(),
                    "".to_string(),
                ));
            } else {
                if !variables.contains_key(&output_content) {
                    panic!("{}", format!("Variable '{}' not declared", output_content));
                }
                ir_code.push((
                    "out_var".to_string(),
                    output_content.clone(),
                    "".to_string(),
                ));
            }
        } else if line.contains("exit") {
            let exit_code = regex::Regex::new(r#"exit\((.*?)\)"#)
                .unwrap()
                .captures(&line)
                .unwrap()[1]
                .trim()
                .to_string();
            ir_code.push(("exit".to_string(), exit_code.clone(), "".to_string()));
        }
    }

    (ir_code, entry_point, variables, functions) // Include functions in the return tuple
}

pub fn generate_assembly_amd64_linux(
    ir_code: Vec<(String, String, String)>,
    entry_point: String,
    variables: HashMap<String, String>,
    _functions: HashMap<String, usize>,
) -> String {
    let mut asm_code = String::from("section .data\n");

    let mut data_idx = 0;
    let mut idx = 0;

    for instruction in ir_code.iter() {
        match instruction.0.as_str() {
            "var" => {
                let (var_name, var_value) = (&instruction.1, &instruction.2);
                asm_code.push_str(&format!("  {} db '{}', 0xA, 0\n\n", var_name, var_value));
                data_idx += 1;
            }
            "out_string" => {
                let string = &instruction.1;
                asm_code.push_str(&format!("  msg_{} db '{}', 0xA, 0\n\n", data_idx, string));
                data_idx += 1;
            }
            _ => {}
        }
    }

    asm_code.push_str("section .text\n");
    asm_code.push_str(&format!("  global {}\n\n", entry_point));

    asm_code.push_str(&format!("{}:\n", entry_point));

    for instruction in ir_code.iter() {
        match instruction.0.as_str() {
            "out_string" => {
                let string = &instruction.1;
                asm_code.push_str("  mov rax, 1\n");
                asm_code.push_str("  mov rdi, 1\n");
                asm_code.push_str(&format!("  lea rsi, [rel msg_{}]\n", idx));
                asm_code.push_str(&format!("  mov rdx, {}\n", string.len() + 1));
                asm_code.push_str("  syscall\n\n");
                idx += 1;
            }
            "out_int" => {
                let int_value = &instruction.1;
                asm_code.push_str("  mov rax, 1\n");
                asm_code.push_str("  mov rdi, 1\n");
                asm_code.push_str(&format!("  mov rsi, {}\n", int_value));
                asm_code.push_str("  mov rdx, 10\n");
                asm_code.push_str("  syscall\n\n");
            }
            "out_var" => {
                let var_name = &instruction.1;
                let content = variables.get(var_name).unwrap();
                asm_code.push_str("  mov rax, 1\n");
                asm_code.push_str("  mov rdi, 1\n");
                asm_code.push_str(&format!("  mov rsi, {}\n", var_name));
                asm_code.push_str(&format!("  mov rdx, {}\n", content.len() + 1));
                asm_code.push_str("  syscall\n\n");
            }
            "exit" => {
                let exit_code = &instruction.1;
                asm_code.push_str(&format!("  mov rax, {}\n", exit_code));
                asm_code.push_str("  mov rdi, rax\n");
                asm_code.push_str("  mov rax, 60\n");
                asm_code.push_str("  syscall\n");
            }
            _ => {}
        }
    }

    asm_code
}

pub fn generate_assembly(lines: &[&str], entry_point: &str) -> String {
    let (ir_code, _, variables, functions) = tokenizer_ir(lines);
    let architecture = std::env::consts::ARCH;
    let platform = std::env::consts::OS;

    match platform {
        "linux" => {
            if architecture == "x86_64" || architecture == "amd64" || architecture == "x86-64" {
                generate_assembly_amd64_linux(
                    ir_code,
                    entry_point.to_string(),
                    variables,
                    functions,
                )
            } else {
                panic!("Unsupported architecture for Linux");
            }
        }
        "windows" => {
            if architecture == "x86_64" || architecture == "amd64" || architecture == "x86-64" {
                unimplemented!("Windows assembly generation not implemented yet");
            } else {
                panic!("Unsupported architecture for Windows");
            }
        }
        _ => panic!("Unsupported platform"),
    }
}
