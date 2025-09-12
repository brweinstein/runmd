use anyhow::Result;
use regex::Regex;
use std::sync::LazyLock;

use crate::config::Config;
use crate::languages::Languages;
use crate::runner::run_code;

/// Match any fenced code block with a language identifier.
static CODE_BLOCK_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"```(\w+)\n([\s\S]*?)```").unwrap()
});

/// Match code block + its output block for removal.
static OUTPUT_BLOCK_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(
        r"(```\w+\n[\s\S]*?```)(?:\n)?\*\*Output:?\*\*\n```[\s\S]*?```(?:\n)?"
    ).unwrap()
});

/// Used to trim trailing newlines inside code blocks.
static TRAILING_NEWLINES_RE: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"```(\w+)\n([\s\S]*?)```").unwrap()
});

/// Detect consecutive backtick fences with no blank line between them.
static CONSECUTIVE_FENCES_RE1: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"``````").unwrap()
});

static CONSECUTIVE_FENCES_RE2: LazyLock<Regex> = LazyLock::new(|| {
    Regex::new(r"```\n```").unwrap()
});

/// Process markdown by executing code blocks and attaching outputs.
pub async fn process_markdown(content: &str) -> Result<String> {
    let config = Config::load()?;
    let languages = Languages::new(config.languages);

    // Step 1: sanitize content by stripping outputs & fixing fences
    let content = clear_outputs(content)?;

    // Step 2: iterate over code blocks and run them
    let mut result = String::new();
    let mut last_end = 0;

    for captures in CODE_BLOCK_RE.captures_iter(&content) {
        let full_match = captures.get(0).unwrap();
        let language = captures.get(1).unwrap().as_str();
        let code = captures.get(2).unwrap().as_str();

        // Preserve text before this code block
        result.push_str(&content[last_end..full_match.start()]);

        // Run the code snippet
        let output = run_code(language, code, &languages, 10).await?;

        // Rebuild the code block with proper fence formatting
        let code_fence = if code.ends_with('\n') {
            format!("```{}\n{}```", language, code)
        } else {
            format!("```{}\n{}\n```", language, code)
        };

        // Append output
        let output_text = output.trim_end_matches('\n');
        let output_block = format!("**Output**\n```\n{}\n```", output_text);

        result.push_str(&format!("{}\n{}", code_fence, output_block));

        last_end = full_match.end();
    }

    // Append any trailing content after the last code block
    result.push_str(&content[last_end..]);

    Ok(result)
}

pub fn clear_outputs(content: &str) -> Result<String> {
    // Remove output blocks following code blocks
    let cleaned = OUTPUT_BLOCK_RE.replace_all(content, "$1");

    // Trim trailing newlines inside code fences
    let cleaned = TRAILING_NEWLINES_RE.replace_all(&cleaned, |caps: &regex::Captures| {
        let language = &caps[1];
        let code = caps[2].trim_end_matches('\n');
        format!("```{}\n{}\n```", language, code)
    });

    // Ensure spacing between consecutive fences
    let cleaned = CONSECUTIVE_FENCES_RE1.replace_all(&cleaned, "```\n\n```");
    let cleaned = CONSECUTIVE_FENCES_RE2.replace_all(&cleaned, "```\n\n```");

    Ok(cleaned.to_string())
}