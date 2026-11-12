---
type: tool_order
before:
  tool: Bash
  input_match: "unittest|test_slug"
after:
  tool: Write
  input_match: '"file_path"\s*:\s*"(?:[^"]*[/\\])?slug\.py"'
---
