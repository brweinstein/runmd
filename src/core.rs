use anyhow::Result;

use crate::config::Config;
use crate::languages::Languages;
use crate::runner::run_code;

#[derive(Debug, Clone)]
struct CodeBlock {
    language: String,
    code: String,
    start_pos: usize,
    end_pos: usize,
    skip: bool,
    fence_info: String,
}

fn find_all_code_blocks(content: &str) -> Vec<CodeBlock> {
    let mut blocks = Vec::new();
    let lines: Vec<&str> = content.lines().collect();
    let mut i = 0;

    while i < lines.len() {
        let line = lines[i].trim();

        // Check if this line starts a code block
        if line.starts_with("```") && line.len() > 3 {
            let info = line[3..].trim();
            let fence_info = info.to_string();

            // Split info string by whitespace to detect modifiers
            let mut skip = false;
            let mut language = String::new();
            if !info.is_empty() {
                let parts: Vec<&str> = info.split_whitespace().collect();
                if !parts.is_empty() {
                    language = parts[0].to_string();
                    for p in &parts[1..] {
                        if *p == "-nr" || *p == "--no-run" {
                            skip = true;
                        }
                    }
                }
            }

            // Validate language token (must exist)
            if language.is_empty()
                || !language
                    .chars()
                    .all(|c| c.is_alphanumeric() || c == '_' || c == '-')
            {
                i += 1;
                continue;
            }

            let start_line = i;
            i += 1; // Move past the opening fence

            // Find the closing fence
            let mut code_lines = Vec::new();
            let mut found_closing = false;
            let mut end_line = i;

            while i < lines.len() {
                if lines[i].trim() == "```" {
                    found_closing = true;
                    end_line = i;
                    break;
                }
                code_lines.push(lines[i]);
                i += 1;
            }

            if found_closing {
                let code = code_lines.join("\n");

                // Calculate character positions (approximate)
                let start_pos = lines[..start_line]
                    .iter()
                    .map(|l| l.len() + 1)
                    .sum::<usize>();
                let end_pos = lines[..=end_line]
                    .iter()
                    .map(|l| l.len() + 1)
                    .sum::<usize>();

                blocks.push(CodeBlock {
                    language: language.to_string(),
                    code,
                    start_pos,
                    end_pos: end_pos.min(content.len()),
                    skip,
                    fence_info,
                });

                i += 1; // Move past the closing fence
            } else {
                // No closing fence found, skip this block
                break;
            }
        } else {
            i += 1;
        }
    }

    blocks
}

/// Process markdown by executing code blocks and attaching outputs.
/// If force_parallel is true, parallel execution is used when more than one runnable block exists.
pub async fn process_markdown(content: &str, force_parallel: bool) -> Result<String> {
    let config = Config::load()?;
    let languages = Languages::new(config.languages);

    // Step 1: sanitize content by stripping outputs
    let content = clear_outputs(content)?;

    // Step 2: find all code blocks
    let code_blocks = find_all_code_blocks(&content);

    if code_blocks.is_empty() {
        return Ok(content);
    }

    // Count runnable (non-skipped) blocks
    let runnable_count = code_blocks.iter().filter(|b| !b.skip).count();

    // Decide execution strategy
    if runnable_count > 1 && (force_parallel || runnable_count >= 4) {
        return process_markdown_parallel(&content, &code_blocks, &languages).await;
    }
    return process_markdown_sequential(&content, &code_blocks, &languages).await;

    // Parallel execution (disabled for now)
    /*
    // If only one block, process sequentially for simplicity
    if code_blocks.len() == 1 {
        return process_markdown_sequential(&content, &languages).await;
    }

    // Step 3: execute all code blocks in parallel using futures::future::join_all
    use futures::future::join_all;

    let tasks: Vec<_> = code_blocks.iter().map(|block| {
        let block_clone = block.clone();
        let languages_clone = languages.clone();

        async move {
            let output = run_code(&block_clone.language, &block_clone.code, &languages_clone, 10).await?;
            Ok::<(usize, String), anyhow::Error>((block_clone.block_id, output))
        }
    }).collect();

    let results: Result<Vec<_>> = join_all(tasks).await.into_iter().collect();
    let results = results?;

    // Step 4: sort results by block_id and extract outputs
    let mut sorted_results = results;
    sorted_results.sort_by_key(|(block_id, _)| *block_id);
    let outputs: Vec<String> = sorted_results.into_iter().map(|(_, output)| output).collect();

    // Step 5: reconstruct content with outputs
    let mut result = String::new();
    let mut last_pos = 0;

    for (i, block) in code_blocks.iter().enumerate() {
        // Add content before this block
        result.push_str(&content[last_pos..block.start_pos]);

        // Add the code block
        let code_fence = if block.code.ends_with('\n') {
            format!("```{}\n{}```", block.language, block.code)
        } else {
            format!("```{}\n{}\n```", block.language, block.code)
        };

        // Add the output
        let output_text = outputs[i].trim_end_matches('\n');
        let output_block = format!("**Output**\n```\n{}\n```", output_text);

        result.push_str(&format!("{}\n{}", code_fence, output_block));
        last_pos = block.end_pos;
    }

    // Add any remaining content
    result.push_str(&content[last_pos..]);

    Ok(result)
    */
}

/// Sequential processing optimized for performance
async fn process_markdown_sequential(
    content: &str,
    code_blocks: &[CodeBlock],
    languages: &Languages,
) -> Result<String> {
    if code_blocks.is_empty() {
        return Ok(content.to_string());
    }

    // Pre-allocate result string with estimated capacity
    let mut result = String::with_capacity(content.len() * 2);
    let mut last_pos = 0;

    for block in code_blocks {
        // Add content before this block (using efficient slicing)
        result.push_str(&content[last_pos..block.start_pos]);
        if block.skip {
            // Just reproduce the original block without running
            result.push_str("```");
            if !block.fence_info.is_empty() { result.push_str(&block.fence_info); } else { result.push_str(&block.language); }
            result.push('\n');
            result.push_str(&block.code);
            if !block.code.ends_with('\n') {
                result.push('\n');
            }
            result.push_str("```");
        } else {
            // Run the code snippet with optimized timeout
            let timeout = if block.code.len() > 1000 { 10 } else { 5 }; // Shorter timeout for small code
            let output = run_code(&block.language, &block.code, languages, timeout).await?;

            // Build output more efficiently
            result.push_str("```");
            if !block.fence_info.is_empty() { result.push_str(&block.fence_info); } else { result.push_str(&block.language); }
            result.push('\n');
            result.push_str(&block.code);
            if !block.code.ends_with('\n') {
                result.push('\n');
            }
            result.push_str("```\n**Output**\n```\n");

            let output_text = output.trim_end_matches('\n');
            result.push_str(output_text);
            result.push_str("\n```");
        }

        last_pos = block.end_pos;
    }

    // Add any remaining content
    result.push_str(&content[last_pos..]);

    Ok(result)
}

/// Parallel processing for multiple code blocks
async fn process_markdown_parallel(
    content: &str,
    code_blocks: &[CodeBlock],
    languages: &Languages,
) -> Result<String> {
    use futures::future::join_all;

    // Execute all code blocks in parallel
    let tasks: Vec<_> = code_blocks
        .iter()
        .enumerate()
        .filter(|(_, b)| !b.skip)
        .map(|(i, block)| {
            let languages_clone = languages.clone();
            let block_clone = block.clone();
            async move {
                let timeout = if block_clone.code.len() > 1000 { 10 } else { 5 };
                let output = run_code(
                    &block_clone.language,
                    &block_clone.code,
                    &languages_clone,
                    timeout,
                )
                .await?;
                Ok::<(usize, String), anyhow::Error>((i, output))
            }
        })
        .collect();

    let results: Result<Vec<_>> = join_all(tasks).await.into_iter().collect();
    let results = results?;

    // Sort results by original order and extract outputs
    let mut sorted_results = results;
    sorted_results.sort_by_key(|(index, _)| *index);
    let outputs: Vec<String> = sorted_results
        .into_iter()
        .map(|(_, output)| output)
        .collect();

    // Reconstruct content with outputs
    let mut result = String::with_capacity(content.len() * 2);
    let mut last_pos = 0;

    for (i, block) in code_blocks.iter().enumerate() {
        // Add content before this block
        result.push_str(&content[last_pos..block.start_pos]);
        if block.skip {
            // Reproduce original skipped block
            result.push_str("```");
            if !block.fence_info.is_empty() { result.push_str(&block.fence_info); } else { result.push_str(&block.language); }
            result.push('\n');
            result.push_str(&block.code);
            if !block.code.ends_with('\n') {
                result.push('\n');
            }
            result.push_str("```");
        } else {
            // Determine the index in outputs vector based on non-skipped blocks
            // We built outputs only for non-skipped blocks, preserve order.
            // Map i -> position among non-skipped indices
            let non_skipped_index = code_blocks.iter().take(i + 1).filter(|b| !b.skip).count() - 1;
            result.push_str("```");
            if !block.fence_info.is_empty() { result.push_str(&block.fence_info); } else { result.push_str(&block.language); }
            result.push('\n');
            result.push_str(&block.code);
            if !block.code.ends_with('\n') {
                result.push('\n');
            }
            result.push_str("```\n**Output**\n```\n");
            let output_text = outputs[non_skipped_index].trim_end_matches('\n');
            result.push_str(output_text);
            result.push_str("\n```");
        }

        last_pos = block.end_pos;
    }

    // Add any remaining content
    result.push_str(&content[last_pos..]);

    Ok(result)
}

pub fn clear_outputs(content: &str) -> Result<String> {
    // Use simple string replacements for speed - much faster than line parsing
    let mut result = content.to_string();

    // Remove output blocks - pattern: code block + output block
    // This is a simplified approach that should be very fast
    loop {
        let original_len = result.len();

        // Find and remove pattern: ```\n**Output**\n```\n...\n```
        if let Some(output_start) = result.find("\n**Output**\n```") {
            // Work backwards to find the code block end
            let mut code_end = output_start;
            while code_end > 0 && !result[..code_end].ends_with("```") {
                code_end -= 1;
            }

            if code_end > 0 {
                // Find the end of the output block
                let search_start = output_start + 13; // Skip "\n**Output**\n```"
                if let Some(output_end_rel) = result[search_start..].find("\n```") {
                    let output_end = search_start + output_end_rel + 4; // Include "\n```"

                    // Remove the output block (keep the code block)
                    result = format!("{}{}", &result[..output_start], &result[output_end..]);
                    continue;
                }
            }
        }

        // Also handle pattern without leading newline: **Output**\n```
        if let Some(output_start) = result.find("**Output**\n```") {
            let search_start = output_start + 12; // Skip "**Output**\n```"
            if let Some(output_end_rel) = result[search_start..].find("\n```") {
                let output_end = search_start + output_end_rel + 4; // Include "\n```"
                result = format!("{}{}", &result[..output_start], &result[output_end..]);
                continue;
            }
        }

        // If no changes made, we're done
        if result.len() == original_len {
            break;
        }
    }

    // Clean up any consecutive fences (much faster than regex)
    result = result.replace("``````", "```\n\n```");
    result = result.replace("```\n```", "```\n\n```");

    Ok(result)
}
