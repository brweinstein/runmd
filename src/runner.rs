use anyhow::{Context, Result};
use std::time::Duration;
use tempfile::NamedTempFile;
use tokio::process::Command;
use tokio::time::timeout;

use crate::languages::Languages;

pub async fn run_code(
    language: &str,
    code: &str,
    languages: &Languages,
    timeout_secs: u64,
) -> Result<String> {
    // Get command template for the language
    let temp_file = create_temp_file(language, code)?;
    let file_path = temp_file.path().to_string_lossy().to_string();

    let command_parts = match languages.get_command(language, &file_path) {
        Some(parts) => parts,
        None => return Ok(format!("[error] Language '{}' not supported.", language)),
    };

    if command_parts.is_empty() {
        return Ok("[error] Invalid command configuration.".to_string());
    }

    // Check if the required executable exists
    if !languages.check_dependency_exists(&command_parts) {
        return Ok(format!(
            "[error] Required interpreter/compiler for '{}' is not installed.",
            language
        ));
    }

    // Special handling for Racket - add #lang directive if missing
    if language.to_lowercase() == "racket" && !code.trim_start().starts_with("#lang") {
        let modified_code = format!("#lang racket\n{}", code);
        std::fs::write(&file_path, modified_code)?;
    }

    // Execute the command with timeout
    let mut cmd = Command::new(&command_parts[0]);
    if command_parts.len() > 1 {
        cmd.args(&command_parts[1..]);
    }

    let execution_future = cmd.output();
    let timeout_duration = Duration::from_secs(timeout_secs);

    match timeout(timeout_duration, execution_future).await {
        Ok(Ok(output)) => {
            let stdout = String::from_utf8_lossy(&output.stdout);
            let stderr = String::from_utf8_lossy(&output.stderr);

            if output.status.success() || !stdout.is_empty() {
                Ok(stdout.trim().to_string())
            } else {
                Ok(stderr.trim().to_string())
            }
        }
        Ok(Err(e)) => Ok(format!("[error] {}", e)),
        Err(_) => Ok("[error] execution timed out".to_string()),
    }
}

fn create_temp_file(language: &str, code: &str) -> Result<NamedTempFile> {
    let suffix = if language.chars().all(|c| c.is_alphanumeric()) {
        format!(".{}", language)
    } else {
        String::new()
    };

    let mut temp_file = NamedTempFile::with_suffix(&suffix)
        .context("Failed to create temporary file")?;

    std::io::Write::write_all(&mut temp_file, code.as_bytes())
        .context("Failed to write to temporary file")?;

    std::io::Write::flush(&mut temp_file)
        .context("Failed to flush temporary file")?;

    Ok(temp_file)
}