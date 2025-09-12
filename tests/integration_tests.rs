use assert_cmd::Command;
use predicates::prelude::*;
use std::fs;
use tempfile::TempDir;

#[test]
fn test_cli_help() {
    let mut cmd = Command::cargo_bin("runmd").unwrap();
    cmd.arg("--help");
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("Run code blocks inside Markdown"));
}

#[test]
fn test_init_config() {
    let temp_dir = TempDir::new().unwrap();
    std::env::set_var("HOME", temp_dir.path());
    
    let mut cmd = Command::cargo_bin("runmd").unwrap();
    cmd.arg("--init-config");
    cmd.assert()
        .success()
        .stdout(predicate::str::contains("Wrote default config"));
}

#[test]
fn test_basic_functionality() {
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.md");
    
    // Test with a very simple echo command that should work quickly
    let content = r#"# Test

```bash
echo "hello"
```"#;
    
    fs::write(&test_file, content).unwrap();
    
    let mut cmd = Command::cargo_bin("runmd").unwrap();
    cmd.arg(test_file.to_str().unwrap());
    cmd.timeout(std::time::Duration::from_secs(10)); // Short timeout
    
    let output = cmd.output().unwrap();
    
    // Debug: print what happened
    println!("Exit status: {}", output.status);
    println!("Stdout: {}", String::from_utf8_lossy(&output.stdout));
    println!("Stderr: {}", String::from_utf8_lossy(&output.stderr));
    
    if !output.status.success() {
        panic!("Command failed with status: {}", output.status);
    }
    
    let result = fs::read_to_string(&test_file).unwrap();
    println!("File contents after processing: {}", result);
    assert!(result.contains("**Output**"));
    assert!(result.contains("hello"));
}

#[test]
fn test_process_markdown_file() {
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.md");
    
    let content = r#"# Test

```python
print("hello world")
```"#;
    
    fs::write(&test_file, content).unwrap();
    
    let mut cmd = Command::cargo_bin("runmd").unwrap();
    cmd.arg(test_file.to_str().unwrap());
    cmd.timeout(std::time::Duration::from_secs(30)); // 30 second timeout
    cmd.assert().success();
    
    let result = fs::read_to_string(&test_file).unwrap();
    assert!(result.contains("**Output**"));
    assert!(result.contains("hello world"));
}

#[test]
fn test_clear_outputs() {
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.md");
    
    let content = r#"# Test

```python
print("hello")
```
**Output**
```
hello
```"#;
    
    fs::write(&test_file, content).unwrap();
    
    let mut cmd = Command::cargo_bin("runmd").unwrap();
    cmd.arg("-c").arg(test_file.to_str().unwrap());
    cmd.timeout(std::time::Duration::from_secs(5)); // Should be fast
    cmd.assert().success();
    
    let result = fs::read_to_string(&test_file).unwrap();
    assert!(!result.contains("**Output**"));
    assert!(!result.contains("hello\n```"));
}

#[test]
fn test_error_handling() {
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.md");
    
    let content = r#"# Test

```python
print("test")
raise Exception("error")
```"#;
    
    fs::write(&test_file, content).unwrap();
    
    let mut cmd = Command::cargo_bin("runmd").unwrap();
    cmd.arg(test_file.to_str().unwrap());
    cmd.timeout(std::time::Duration::from_secs(30)); // 30 second timeout
    cmd.assert().success();
    
    let result = fs::read_to_string(&test_file).unwrap();
    assert!(result.contains("**Output**"));
    assert!(result.contains("Exception"));
}

#[test]
fn test_multiple_code_blocks() {
    let temp_dir = TempDir::new().unwrap();
    let test_file = temp_dir.path().join("test.md");
    
    let content = r#"# Test

```python
print("block 1")
```

```python
print("block 2")
```

```python  
print("block 3")
```"#;
    
    fs::write(&test_file, content).unwrap();
    
    let mut cmd = Command::cargo_bin("runmd").unwrap();
    cmd.arg(test_file.to_str().unwrap());
    cmd.timeout(std::time::Duration::from_secs(45)); // Longer timeout for multiple blocks
    cmd.assert().success();
    
    let result = fs::read_to_string(&test_file).unwrap();
    assert_eq!(result.matches("**Output**").count(), 3); // Should have 3 output blocks
    assert!(result.contains("block 1"));
    assert!(result.contains("block 2"));
    assert!(result.contains("block 3"));
}