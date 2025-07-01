# Feature Flag Dependency Analysis System

## Overview

This project supports automated detection, analysis, and visualization of feature flag (toggle) usage and dependencies in multi-language (Python/Java/Go/JS/TS) codebases, including support for CloudBees, Unleash, and other mainstream solutions.

## Features

- Automatically extract feature flag usage points, supporting multiple languages and invocation styles
- Cross-file/module dependency analysis and cycle detection
- Interactive HTML dependency graph visualization
- Extensible Semgrep rules for different flag frameworks

## Quick Start

### 1. Install Dependencies

```sh
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
```

> It is recommended to use pyvis==0.1.9 to avoid template issues in some environments.

### 2. Configure Scan Rules

- Rule files are in `semgrep_rules/`, e.g.:
  - `python-feature-flags.yml`, `go-feature-flags.yml`, `unleash-feature-flags.yml`
- For Unleash/CloudBees/Go projects, `unleash-feature-flags.yml` supports the following invocation styles:
  - Java/JS/TS: `obj.isEnabled(flag)`, `obj.getVariant(flag)`
  - Python: `obj.is_enabled(flag)`, `obj.get_variant(flag)`
  - Go: `obj.IsEnabled(flag)`, `obj.GetVariant(flag)`

### 3. Scan Projects

For example, to scan a CloudBees Go project and an Unleash multi-language project:

```sh
# Scan CloudBees Go project
semgrep --config semgrep_rules/go-feature-flags.yml /Users/weimingzhuang/Documents/source_code/CloudBees-sample-Go-app --json > go_scan_result.json

# Scan Unleash multi-language project
semgrep --config semgrep_rules/unleash-feature-flags.yml /Users/weimingzhuang/Documents/source_code/unleash-managed-projects-sample --json > unleash_scan_result.json
```

### 4. View Scan Results

- CloudBees Go project: 2 feature flag usage points detected (in main.go)
- Unleash project: 2 feature flag usage points detected (in Java/JS code)
- Results are in `go_scan_result.json` and `unleash_scan_result.json`, which can be further used for dependency analysis and visualization.

### 5. Dependency Analysis & Visualization

To automatically generate the dependency graph and interactive HTML, add your target project paths to the scan directory configuration in `src/main.py`, then run:

```sh
python3 src/main.py
```

This will generate `dependency_graph.html`, which you can open in your browser to interactively explore flag distribution and dependencies.

## Rule Extension & Adaptation

- You can edit `semgrep_rules/*.yml` to match your actual flag framework and invocation style, using `pattern-either` for multi-pattern matching.
- Supports Java, Go, Python, JS/TS, and more.

## Example Scan Rule (unleash-feature-flags.yml)

```yaml
rules:
  - id: unleash-feature-flag
    patterns:
      - pattern-either:
          - pattern: $OBJ.isEnabled($FLAG, ...)
          - pattern: $OBJ.isEnabled($FLAG)
          - pattern: $OBJ.getVariant($FLAG, ...)
          - pattern: $OBJ.getVariant($FLAG)
          - pattern: $OBJ.is_enabled($FLAG, ...)
          - pattern: $OBJ.is_enabled($FLAG)
          - pattern: $OBJ.get_variant($FLAG, ...)
          - pattern: $OBJ.get_variant($FLAG)
          - pattern: $OBJ.IsEnabled($FLAG, ...)
          - pattern: $OBJ.IsEnabled($FLAG)
          - pattern: $OBJ.GetVariant($FLAG, ...)
          - pattern: $OBJ.GetVariant($FLAG)
    message: Found Unleash feature flag usage
    languages: [java, javascript, typescript, python, go]
    severity: INFO
```

## Result Interpretation

- The scan results will output all flag usage points (file, line number, invocation style), and can extract even single-flag usage automatically.
- You can combine with the dependency analysis script to automatically generate a dependency graph.
