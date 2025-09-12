#!/usr/bin/env python3
"""
Benchmark script to compare Python and Rust implementations of runmd.
Generates test markdown files and measures execution time for various operations.
"""

import os
import sys
import time
import tempfile
import subprocess
from pathlib import Path

# Add the core module to path for Python version
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_test_markdown(num_blocks: int, block_size: int = 5, use_simple_code: bool = False) -> str:
   """Create a markdown file with the specified number of code blocks."""
   content = "# Performance Test\n\n"
   
   for i in range(num_blocks):
      content += f"## Block {i+1}\n\n"
      content += "```python\n"
      if use_simple_code:
         # Simple code that executes quickly
         content += f"print({i+1})\n"
      else:
         for j in range(block_size):
            content += f"print('Block {i+1}, line {j+1}')\n"
      content += "```\n\n"
   
   return content

def create_large_markdown(size_mb: float) -> str:
   """Create a large markdown file of approximately the specified size."""
   base_block = """## Test Section

Some explanatory text here.

```python
print("Hello world")
x = 1 + 1
print(f"Result: {x}")
```

More text content here to fill space.

```bash
echo "Shell command"
ls -la
```

"""
   
   target_size = int(size_mb * 1024 * 1024)  # Convert to bytes
   content = "# Large Performance Test\n\n"
   
   while len(content) < target_size:
      content += base_block
   
   return content

def time_operation(operation_name: str, func):
   """Time an operation and return the result and elapsed time."""
   start_time = time.time()
   result = func()
   end_time = time.time()
   elapsed = (end_time - start_time) * 1000  # Convert to milliseconds
   print(f"{operation_name}: {elapsed:.1f}ms")
   return result, elapsed

def benchmark_python_version():
   """Benchmark the Python implementation."""
   print("Benchmarking Python version...")
   
   try:
      print("  Importing Python modules...")
      from core.core import process_markdown, clear_outputs
      print("  Python modules imported successfully")
      
      # Test 1: Parse large markdown
      print("  Creating large markdown content (1MB)...")
      large_content = create_large_markdown(1.0)  # 1MB
      print("  Running Python parse test...")
      _, parse_time = time_operation("Python parse 1MB", lambda: clear_outputs(large_content))
      
      # Test 2: Execute code blocks
      print("  Creating small test content (3 blocks, simple code)...")
      small_content = create_test_markdown(3, 1, use_simple_code=True)  # 3 very simple blocks
      print("  Running Python execution test...")
      _, exec_time = time_operation("Python execute 3 blocks", lambda: process_markdown(small_content))
      
      # Test 3: Clear outputs
      print("  Creating content with outputs (50 blocks)...")
      content_with_outputs = create_test_markdown(50, 1)
      # Simulate processed content with outputs
      content_with_outputs = content_with_outputs.replace("```\n\n", "```\n**Output**\n```\ntest output\n```\n\n")
      print("  Running Python clear outputs test...")
      _, clear_time = time_operation("Python clear 50 outputs", lambda: clear_outputs(content_with_outputs))
      
      return {
         'parse_1mb': parse_time,
         'execute_3_blocks': exec_time,
         'clear_50_outputs': clear_time
      }
      
   except ImportError as e:
      print(f"Could not import Python modules: {e}")
      return None

def benchmark_rust_version():
   """Benchmark the Rust implementation."""
   print("Benchmarking Rust version...")
   
   rust_binary = Path(__file__).parent.parent / "target" / "release" / "runmd"
   print(f"  Checking for Rust binary at: {rust_binary}")
   if not rust_binary.exists():
      print("Rust binary not found. Run 'cargo build --release' first.")
      return None
   print("  Rust binary found")
   
   results = {}
   
   with tempfile.TemporaryDirectory() as temp_dir:
      print(f"  Using temporary directory: {temp_dir}")
      
      # Test 1: Parse large markdown (using clear operation as proxy)
      print("  Creating large markdown file for Rust test...")
      large_file = Path(temp_dir) / "large.md"
      large_content = create_large_markdown(1.0)
      large_file.write_text(large_content)
      print("  Large file created")
      
      def rust_parse():
         result = subprocess.run([str(rust_binary), "-c", str(large_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust parse failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, parse_time = time_operation("Rust parse 1MB", rust_parse)
      results['parse_1mb'] = parse_time
      
      # Test 2: Execute code blocks
      print("  Creating execution test file...")
      exec_file = Path(temp_dir) / "exec.md"
      exec_content = create_test_markdown(3, 1, use_simple_code=True)
      exec_file.write_text(exec_content)
      print("  Execution file created")
      
      def rust_execute():
         result = subprocess.run([str(rust_binary), str(exec_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust execution failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, exec_time = time_operation("Rust execute 3 blocks", rust_execute)
      results['execute_3_blocks'] = exec_time
      
      # Test 3: Clear outputs
      clear_file = Path(temp_dir) / "clear.md"
      clear_content = create_test_markdown(50, 1)
      # Simulate content with outputs
      clear_content = clear_content.replace("```\n\n", "```\n**Output**\n```\ntest output\n```\n\n")
      clear_file.write_text(clear_content)
      
      def rust_clear():
         result = subprocess.run([str(rust_binary), "-c", str(clear_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust clear failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, clear_time = time_operation("Rust clear 50 outputs", rust_clear)
      results['clear_50_outputs'] = clear_time
   
   return results

def format_results(python_results, rust_results):
   """Format and display comparison results."""
   print("\n" + "="*60)
   print("PERFORMANCE COMPARISON RESULTS")
   print("="*60)
   
   if not python_results:
      print("Python results not available")
      return
   
   if not rust_results:
      print("Rust results not available")
      return
   
   print(f"{'Operation':<25} {'Python':<12} {'Rust':<12} {'Speedup':<10}")
   print("-" * 60)
   
   operations = [
      ('parse_1mb', 'Parse 1MB markdown'),
      ('execute_3_blocks', 'Execute 3 blocks'),
      ('clear_50_outputs', 'Clear 50 outputs')
   ]
   
   for key, description in operations:
      python_time = python_results.get(key, 0)
      rust_time = rust_results.get(key, 0)
      
      if rust_time > 0:
         speedup = python_time / rust_time
         print(f"{description:<25} {python_time:>8.1f}ms {rust_time:>8.1f}ms {speedup:>8.1f}x")
      else:
         print(f"{description:<25} {python_time:>8.1f}ms {'N/A':<8} {'N/A':<8}")
   
   print("\nFor README.md table format:")
   print("| Operation | Python Version | Rust Version | Speedup |")
   print("|-----------|---------------|--------------|---------|")
   
   for key, description in operations:
      python_time = python_results.get(key, 0)
      rust_time = rust_results.get(key, 0)
      
      if rust_time > 0:
         speedup = python_time / rust_time
         print(f"| {description} | {python_time:.0f}ms | **{rust_time:.0f}ms** | **{speedup:.1f}x** |")

def main():
   print("runmd Performance Benchmark")
   print("==========================")
   
   # Build Rust version if it doesn't exist
   rust_binary = Path(__file__).parent.parent / "target" / "release" / "runmd"
   if not rust_binary.exists():
      print("Building Rust version...")
      result = subprocess.run(
         ["cargo", "build", "--release"], 
         cwd=Path(__file__).parent.parent,
         capture_output=True
      )
      if result.returncode != 0:
         print("Failed to build Rust version")
         print(result.stderr.decode())
         sys.exit(1)
   
   python_results = benchmark_python_version()
   rust_results = benchmark_rust_version()
   
   format_results(python_results, rust_results)

if __name__ == "__main__":
   main()