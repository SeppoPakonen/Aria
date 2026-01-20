# 40-settings-help-man.md

This runbook details `aria`'s commands for accessing internal information: settings, tutorials, manual pages, general help, and version information. These tools are invaluable for understanding `aria`'s configuration, learning its features, and troubleshooting.

## `aria settings`

Displays the current configuration settings of the `aria` CLI. This includes paths to Aria home, active browsers, log levels, and default AI providers. It's useful for verifying your setup or diagnosing unexpected behavior.

```bash
# Linux/macOS & Windows CMD
aria settings
```

## `aria settings export-artifacts`

Packages all execution artifacts (logs, reports, session metadata) into a single ZIP archive. This is particularly useful for collecting diagnostics in CI/CD environments or when reporting bugs.

```bash
# Linux/macOS & Windows CMD
aria settings export-artifacts --path my-run.zip
```
Note: Sensitive information like `credentials.json` is automatically excluded from the archive.


**Sample Output Expectation (Generic Description)**:
The output will typically be a structured list (e.g., JSON, YAML, or key-value pairs) showing various configurable options and their current values. It will not be an exact output, but will reflect the state of `aria`'s internal settings.

## `aria tutorial`

Launches an interactive tutorial or guided tour of `aria`'s features. This is the best starting point for new users or for those who want a structured walkthrough of common workflows.

```bash
# Linux/macOS & Windows CMD
aria tutorial
```

**Sample Output Expectation (Generic Description)**:
This command will likely initiate a step-by-step guide directly within your terminal, prompting you to try out various `aria` commands and explaining their functionality as you go.

## `aria man`

Displays detailed manual pages for `aria`, similar to traditional Unix `man` pages. This provides comprehensive documentation on all commands, subcommands, arguments, and options. It's a deep dive into `aria`'s capabilities.

```bash
# Linux/macOS & Windows CMD
aria man
```

**Sample Output Expectation (Generic Description)**:
The output will be extensive, covering the purpose of `aria`, a list of all top-level commands, detailed descriptions for each command (e.g., `page`, `script`, `open`), their respective arguments and flags, and possibly examples. It's an exhaustive reference.

## `aria {help|-h|--help}`

Provides a brief overview of `aria`'s commands and general usage. This is a quick reference for when you need to remember a command's basic syntax or available options.

```bash
# Linux/macOS & Windows CMD
aria help
aria -h
aria --help
```
You can also get help for specific subcommands:
```bash
# Linux/macOS & Windows CMD: Get help for the 'page' subcommand
aria page --help
```

**Sample Output Expectation (Generic Description)**:
A concise summary of `aria`'s primary commands, their arguments, and short descriptions. For subcommand help, it will list options pertinent to that specific subcommand.

## `aria {version|-v|--version}`

Displays the current version of the `aria` CLI tool. Useful for bug reporting or ensuring you are running the expected software version.

```bash
# Linux/macOS & Windows CMD
aria version
aria -v
aria --version
```

**Sample Output Expectation (Generic Description)**:
A simple string indicating the version number, e.g., `aria CLI version 1.2.3`.

## Troubleshooting Checklist

When encountering issues with `aria`, these commands can help you diagnose and resolve problems:

1.  **Check `aria settings`**: Verify that your configuration matches expectations (e.g., browser paths, default profiles).
2.  **Review `aria man` or `aria help`**: Ensure you are using the correct syntax and understanding the command's expected behavior. Misspellings or incorrect arguments are common sources of errors.
3.  **Consult `aria tutorial`**: If you're new to a feature, the tutorial might guide you through the correct steps and common pitfalls.
4.  **Verify `aria version`**: If you suspect a bug, noting the version number is crucial for reporting the issue accurately.
