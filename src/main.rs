use anyhow::Result;
use clap::{Arg, Command};
use std::path::PathBuf;

mod config;
mod core;
mod languages;
mod runner;

use crate::config::Config;
use crate::core::{clear_outputs, process_markdown};

#[tokio::main]
async fn main() -> Result<()> {
    let matches = Command::new("runmd")
        .version("0.2.0")
        .about("Run code blocks inside Markdown files and insert their outputs inline")
        .arg(
            Arg::new("file")
                .help("Markdown file to process")
                .required_unless_present("init-config")
                .index(1),
        )
        .arg(
            Arg::new("clear")
                .short('c')
                .long("clear")
                .help("Clear outputs only")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("init-config")
                .long("init-config")
                .help("Create ~/.config/runmd/languages.config with sensible defaults")
                .action(clap::ArgAction::SetTrue),
        )
        .arg(
            Arg::new("parallel")
                .short('p')
                .long("parallel")
                .help("Force parallel execution when more than one runnable code block present")
                .action(clap::ArgAction::SetTrue),
        )
        .get_matches();

    if matches.get_flag("init-config") {
        let config_path = Config::default_config_path()?;
        Config::write_default_config(&config_path)?;
        println!("Wrote default config to {}", config_path.display());
        return Ok(());
    }

    let file_path = matches
        .get_one::<String>("file")
        .map(PathBuf::from)
        .unwrap();

    let content = std::fs::read_to_string(&file_path)?;

    let force_parallel = matches.get_flag("parallel");

    let result = if matches.get_flag("clear") {
        clear_outputs(&content)?
    } else {
        process_markdown(&content, force_parallel).await?
    };

    std::fs::write(&file_path, result)?;

    if matches.get_flag("clear") {
        println!("Cleared outputs in {}", file_path.display());
    } else {
        println!("Processed {}", file_path.display());
    }

    Ok(())
}
