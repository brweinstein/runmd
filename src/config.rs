use anyhow::{Context, Result};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub languages: HashMap<String, String>,
}

impl Config {
    pub fn load() -> Result<Self> {
        let config_path = Self::default_config_path()?;

        if config_path.exists() {
            let content = std::fs::read_to_string(&config_path).with_context(|| {
                format!("Failed to read config file: {}", config_path.display())
            })?;

            let languages: HashMap<String, String> =
                serde_yaml::from_str(&content).with_context(|| "Failed to parse config file")?;

            Ok(Config { languages })
        } else {
            Ok(Self::default())
        }
    }

    pub fn default_config_path() -> Result<PathBuf> {
        let config_dir = dirs::config_dir()
            .context("Could not determine config directory")?
            .join("runmd");

        Ok(config_dir.join("languages.config"))
    }

    pub fn write_default_config(path: &PathBuf) -> Result<()> {
        if let Some(parent) = path.parent() {
            std::fs::create_dir_all(parent)?;
        }

        let default_config = Self::default();
        let content = serde_yaml::to_string(&default_config.languages)?;
        std::fs::write(path, content)?;

        Ok(())
    }
}

impl Default for Config {
    fn default() -> Self {
        let mut languages = HashMap::new();

        languages.insert("python".to_string(), "python3 {file}".to_string());
        languages.insert("py".to_string(), "python3 {file}".to_string());
        languages.insert("racket".to_string(), "racket {file}".to_string());
        languages.insert("bash".to_string(), "bash {file}".to_string());
        languages.insert("sh".to_string(), "sh {file}".to_string());
        languages.insert("javascript".to_string(), "node {file}".to_string());
        languages.insert("js".to_string(), "node {file}".to_string());
        languages.insert("ruby".to_string(), "ruby {file}".to_string());
        languages.insert("php".to_string(), "php {file}".to_string());
        languages.insert("julia".to_string(), "julia {file}".to_string());
        languages.insert("lua".to_string(), "lua {file}".to_string());
        languages.insert("r".to_string(), "Rscript {file}".to_string());
        languages.insert(
            "rust".to_string(),
            "sh -c 'rustc {file} -o /tmp/runmd_rust && /tmp/runmd_rust'".to_string(),
        );
        languages.insert("go".to_string(), "go run {file}".to_string());
        languages.insert(
            "java".to_string(),
            "sh -c 'javac {file} && java $(basename {file} .java)'".to_string(),
        );
        languages.insert(
            "cpp".to_string(),
            "sh -c 'g++ {file} -o /tmp/runmd_cpp && /tmp/runmd_cpp'".to_string(),
        );
        languages.insert(
            "c".to_string(),
            "sh -c 'gcc {file} -o /tmp/runmd_c && /tmp/runmd_c'".to_string(),
        );

        Config { languages }
    }
}
