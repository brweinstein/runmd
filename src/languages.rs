use std::collections::HashMap;
use std::process::Command;

#[derive(Clone)]
pub struct Languages {
   pub mappings: HashMap<String, String>,
}

impl Languages {
   pub fn new(mappings: HashMap<String, String>) -> Self {
      Self { mappings }
   }

   pub fn get_command(&self, language: &str, file_path: &str) -> Option<Vec<String>> {
      self.mappings.get(language).map(|template| {
         let command_str = template.replace("{file}", file_path);
         shell_words::split(&command_str).unwrap_or_else(|_| vec![command_str])
      })
   }

   pub fn check_dependency_exists(&self, command: &[String]) -> bool {
      if command.is_empty() {
         return false;
      }

      let base_cmd = &command[0];
      
      // Handle shell commands
      if base_cmd == "sh" || base_cmd == "bash" {
         return true;
      }

      // Check if the command exists using 'which'
      Command::new("which")
         .arg(base_cmd)
         .output()
         .map(|output| output.status.success())
         .unwrap_or(false)
   }
}

// Simple shell word splitting - for more complex cases, use the shell-words crate
mod shell_words {
   pub fn split(input: &str) -> Result<Vec<String>, ()> {
      let mut words = Vec::new();
      let mut current_word = String::new();
      let mut in_quotes = false;
      let mut escape_next = false;

      for ch in input.chars() {
         if escape_next {
               current_word.push(ch);
               escape_next = false;
         } else if ch == '\\' {
               escape_next = true;
         } else if ch == '"' {
               in_quotes = !in_quotes;
         } else if ch.is_whitespace() && !in_quotes {
               if !current_word.is_empty() {
                  words.push(current_word.clone());
                  current_word.clear();
               }
         } else {
               current_word.push(ch);
         }
      }

      if !current_word.is_empty() {
         words.push(current_word);
      }

      Ok(words)
   }
}