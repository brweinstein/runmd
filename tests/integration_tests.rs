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
    cmd.assert().success();
    
    let result = fs::read_to_string(&test_file).unwrap();
    assert!(result.contains("**Output**"));
    assert!(result.contains("Exception"));
}