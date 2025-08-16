# Petal Examples

This directory contains examples of Petal workflow files demonstrating both the canonical and short-form formats.

## File Formats

### Canonical Format (`canonical_example.yaml`)
The fully expanded, explicit format that the Petal runner executes directly. Contains:
- Explicit step IDs (`shell.run#1`, `llm.generate#1`)
- Declared `reads` and `writes` for each step
- All metadata explicitly defined
- No implicit inference or shortcuts

### Short-Form Format (`.petal` files)
The ergonomic authoring format that gets compiled to canonical form. Features:
- Implicit step IDs (auto-generated from tool name + order)
- Inferred `reads` and `writes` from templates and tool contracts
- Compact syntax with modifiers in parentheses
- Macros for reusable step groups
- Profiles for environment-specific configurations

## Examples

### 1. Basic Workflow (`short_form_example.petal` / `canonical_example.yaml`)
A simple end-to-end workflow that:
1. Runs a shell command to list directory contents
2. Uses an LLM to analyze the output
3. Queries a SQLite database for matching items
4. Posts results to Slack (if any found)
5. Posts a summary to Twitter

**Key features demonstrated:**
- Parameter templating with Jinja2
- Conditional execution (`when` clauses)
- Error handling policies (`if_error=skip`)
- Built-in filters (`truncate`, `rows`)

### 2. Advanced Features (`macro_example.petal`)
Demonstrates more sophisticated Petal capabilities:
- **Macros**: Reusable step groups (`health_check`, `notify_team`)
- **Profiles**: Environment-specific configurations (`dev` vs `prod`)
- **Complex templating**: Multi-line prompts and conditional logic
- **Python integration**: Calling custom functions with `python.eval`

## Running the Examples

```bash
# Validate a short-form file
petal validate examples/short_form_example.petal

# See the compiled canonical form
petal explain examples/short_form_example.petal

# Run the workflow
petal run examples/short_form_example.petal

# Run with parameter overrides
petal run examples/short_form_example.petal -p cmd="ls -la /tmp" -p prompt="Analyze temp directory"
```

## Key Concepts

### State Flow
Each step's output becomes available to subsequent steps via the `state` object:
- `shell.run` writes `shell_out`, `shell_rc`, `shell_err`
- `llm.generate` reads `shell_out` and writes `llm_query`, `text`
- Later steps can reference any previous outputs

### Error Handling
- `if_error=fail` (default): Stop execution on error
- `if_error=skip`: Log error and continue
- `if_error=retry`: Retry with exponential backoff

### Secrets Management
- Secrets are referenced by name only in files
- Resolved from environment variables or OS keyring at runtime
- Automatically redacted in logs and snapshots

### Templating
- Jinja2 templates with custom filters
- Context resolution: `locals → params → state → env → secrets`
- Built-in helpers: `truncate`, `head`, `lines`, `rows`, `now`, `json`

## Next Steps

1. **Install Petal**: Follow the installation instructions in the main README
2. **Set up secrets**: Configure your environment variables for Slack/Twitter
3. **Try the examples**: Start with `short_form_example.petal`
4. **Create your own**: Use these as templates for your workflows
5. **Explore the LSP**: Install `petal-lsp` for editor integration
