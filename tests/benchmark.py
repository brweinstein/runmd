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
      
      results = {}
      
      # Small workload tests
      print("  === SMALL WORKLOAD TESTS ===")
      
      # Test 1: Small parse test
      print("  Creating small markdown content (100KB)...")
      small_content = create_large_markdown(0.1)  # 100KB
      print("  Running Python small parse test...")
      _, small_parse_time = time_operation("Python parse 100KB", lambda: clear_outputs(small_content))
      results['small_parse'] = small_parse_time
      
      # Test 2: Few code blocks
      print("  Creating content with 3 simple blocks...")
      few_blocks_content = create_test_markdown(3, 1, use_simple_code=True)
      print("  Running Python execute 3 blocks test...")
      _, few_exec_time = time_operation("Python execute 3 blocks", lambda: process_markdown(few_blocks_content))
      results['small_execute'] = few_exec_time
      
      # Test 3: Small clear test
      print("  Creating content with outputs (10 blocks)...")
      small_clear_content = create_test_markdown(10, 1)
      small_clear_content = small_clear_content.replace("```\n\n", "```\n**Output**\n```\ntest output\n```\n\n")
      print("  Running Python clear 10 outputs test...")
      _, small_clear_time = time_operation("Python clear 10 outputs", lambda: clear_outputs(small_clear_content))
      results['small_clear'] = small_clear_time
      
      # Large workload tests
      print("  === LARGE WORKLOAD TESTS ===")
      
      # Test 4: Large parse test
      print("  Creating large markdown content (1MB)...")
      large_content = create_large_markdown(1.0)  # 1MB
      print("  Running Python large parse test...")
      _, large_parse_time = time_operation("Python parse 1MB", lambda: clear_outputs(large_content))
      results['large_parse'] = large_parse_time
      
      # Test 5: Many code blocks
      print("  Creating content with 20 simple blocks...")
      many_blocks_content = create_test_markdown(20, 1, use_simple_code=True)
      print("  Running Python execute 20 blocks test...")
      _, many_exec_time = time_operation("Python execute 20 blocks", lambda: process_markdown(many_blocks_content))
      results['large_execute'] = many_exec_time
      
      # Test 6: Large clear test
      print("  Creating content with outputs (100 blocks)...")
      large_clear_content = create_test_markdown(100, 1)
      large_clear_content = large_clear_content.replace("```\n\n", "```\n**Output**\n```\ntest output\n```\n\n")
      print("  Running Python clear 100 outputs test...")
      _, large_clear_time = time_operation("Python clear 100 outputs", lambda: clear_outputs(large_clear_content))
      results['large_clear'] = large_clear_time
      
      return results
      
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
      
      # Small workload tests
      print("  === SMALL WORKLOAD TESTS ===")
      
      # Test 1: Small parse test
      print("  Creating small markdown file...")
      small_file = Path(temp_dir) / "small.md"
      small_content = create_large_markdown(0.1)  # 100KB
      small_file.write_text(small_content)
      
      def rust_small_parse():
         result = subprocess.run([str(rust_binary), "-c", str(small_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust small parse failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, small_parse_time = time_operation("Rust parse 100KB", rust_small_parse)
      results['small_parse'] = small_parse_time
      
      # Test 2: Few code blocks execution
      print("  Creating small execution test file...")
      small_exec_file = Path(temp_dir) / "small_exec.md"
      small_exec_content = create_test_markdown(3, 1, use_simple_code=True)
      small_exec_file.write_text(small_exec_content)
      
      def rust_small_execute():
         result = subprocess.run([str(rust_binary), str(small_exec_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust small execution failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, small_exec_time = time_operation("Rust execute 3 blocks", rust_small_execute)
      results['small_execute'] = small_exec_time
      
      # Test 3: Small clear test
      print("  Creating small clear test file...")
      small_clear_file = Path(temp_dir) / "small_clear.md"
      small_clear_content = create_test_markdown(10, 1)
      small_clear_content = small_clear_content.replace("```\n\n", "```\n**Output**\n```\ntest output\n```\n\n")
      small_clear_file.write_text(small_clear_content)
      
      def rust_small_clear():
         result = subprocess.run([str(rust_binary), "-c", str(small_clear_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust small clear failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, small_clear_time = time_operation("Rust clear 10 outputs", rust_small_clear)
      results['small_clear'] = small_clear_time
      
      # Large workload tests
      print("  === LARGE WORKLOAD TESTS ===")
      
      # Test 4: Large parse test
      print("  Creating large markdown file...")
      large_file = Path(temp_dir) / "large.md"
      large_content = create_large_markdown(1.0)  # 1MB
      large_file.write_text(large_content)
      
      def rust_large_parse():
         result = subprocess.run([str(rust_binary), "-c", str(large_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust large parse failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, large_parse_time = time_operation("Rust parse 1MB", rust_large_parse)
      results['large_parse'] = large_parse_time
      
      # Test 5: Many code blocks execution
      print("  Creating large execution test file...")
      large_exec_file = Path(temp_dir) / "large_exec.md"
      large_exec_content = create_test_markdown(20, 1, use_simple_code=True)
      large_exec_file.write_text(large_exec_content)
      
      def rust_large_execute():
         result = subprocess.run([str(rust_binary), str(large_exec_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust large execution failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, large_exec_time = time_operation("Rust execute 20 blocks", rust_large_execute)
      results['large_execute'] = large_exec_time
      
      # Test 6: Large clear test
      print("  Creating large clear test file...")
      large_clear_file = Path(temp_dir) / "large_clear.md"
      large_clear_content = create_test_markdown(100, 1)
      large_clear_content = large_clear_content.replace("```\n\n", "```\n**Output**\n```\ntest output\n```\n\n")
      large_clear_file.write_text(large_clear_content)
      
      def rust_large_clear():
         result = subprocess.run([str(rust_binary), "-c", str(large_clear_file)], 
                                 capture_output=True, text=True)
         if result.returncode != 0:
               print(f"Rust large clear failed: {result.stderr}")
               raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)
      
      _, large_clear_time = time_operation("Rust clear 100 outputs", rust_large_clear)
      results['large_clear'] = large_clear_time
   
   return results

def format_results(python_results, rust_results):
   """Format and display comparison results."""
   print("\n" + "="*80)
   print("PERFORMANCE COMPARISON RESULTS")
   print("="*80)
   
   if not python_results:
      print("Python results not available")
      return
   
   if not rust_results:
      print("Rust results not available")
      return
   
   # Small workload results
   print("\n🚀 SMALL WORKLOAD PERFORMANCE:")
   print(f"{'Operation':<30} {'Python':<12} {'Rust':<12} {'Speedup':<10}")
   print("-" * 70)
   
   small_operations = [
      ('small_parse', 'Parse 100KB markdown'),
      ('small_execute', 'Execute 3 code blocks'),
      ('small_clear', 'Clear 10 output blocks')
   ]
   
   for key, description in small_operations:
      python_time = python_results.get(key, 0)
      rust_time = rust_results.get(key, 0)
      
      if rust_time > 0 and python_time > 0:
         speedup = python_time / rust_time
         print(f"{description:<30} {python_time:>8.1f}ms {rust_time:>8.1f}ms {speedup:>8.1f}x")
      else:
         print(f"{description:<30} {python_time:>8.1f}ms {rust_time:>8.1f}ms {'N/A':<8}")
   
   # Large workload results
   print("\n📊 LARGE WORKLOAD PERFORMANCE:")
   print(f"{'Operation':<30} {'Python':<12} {'Rust':<12} {'Speedup':<10}")
   print("-" * 70)
   
   large_operations = [
      ('large_parse', 'Parse 1MB markdown'),
      ('large_execute', 'Execute 20 code blocks'),
      ('large_clear', 'Clear 100 output blocks')
   ]
   
   for key, description in large_operations:
      python_time = python_results.get(key, 0)
      rust_time = rust_results.get(key, 0)
      
      if rust_time > 0 and python_time > 0:
         speedup = python_time / rust_time
         print(f"{description:<30} {python_time:>8.1f}ms {rust_time:>8.1f}ms {speedup:>8.1f}x")
      else:
         print(f"{description:<30} {python_time:>8.1f}ms {rust_time:>8.1f}ms {'N/A':<8}")
   
   # Overall summary
   print("\n📈 SUMMARY:")
   all_operations = small_operations + large_operations
   total_speedups = []
   
   for key, description in all_operations:
      python_time = python_results.get(key, 0)
      rust_time = rust_results.get(key, 0)
      
      if rust_time > 0 and python_time > 0:
         speedup = python_time / rust_time
         total_speedups.append(speedup)
   
   if total_speedups:
      avg_speedup = sum(total_speedups) / len(total_speedups)
      max_speedup = max(total_speedups)
      min_speedup = min(total_speedups)
      print(f"Average speedup: {avg_speedup:.1f}x")
      print(f"Maximum speedup: {max_speedup:.1f}x")
      print(f"Minimum speedup: {min_speedup:.1f}x")
   
   print("\n📋 README.md TABLE FORMAT:")
   print("| Operation | Python Version | Rust Version | Speedup |")
   print("|-----------|---------------|--------------|---------|")
   
   # Use the most impressive results for README
   readme_operations = [
      ('large_parse', 'Parse 1MB markdown'),
      ('large_execute', 'Execute 20 blocks'),
      ('large_clear', 'Clear 100 outputs')
   ]
   
   for key, description in readme_operations:
      python_time = python_results.get(key, 0)
      rust_time = rust_results.get(key, 0)
      
      if rust_time > 0 and python_time > 0:
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