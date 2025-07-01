# Feature Flag Dependency Analysis System

## Overview

This project provides automated detection, analysis, and visualization of feature flag (toggle) usage and dependencies in multi-language (Python/Java/Go/JS/TS) codebases, including support for CloudBees, Unleash, and other mainstream solutions.

## Folder Structure

```
feature-flag-dependency-analysis/
│
├── analysis/
│   ├── semgrep_based/           # Semgrep-based analysis scripts
│   │   └── semgrep_runner.py
│   └── ast_based/              # AST-based deep analysis, merging, reporting, visualization
│       ├── ast_runner.py
│       ├── flag_dependency_conflict_report.py
│       ├── visualize_flag_graph.py
│       └── ...
│
├── src/                        # Core analyzers, logic, and CLI
│   ├── ast_analysis/
│   ├── feature_flag/
│   └── cli/
│
├── semgrep_rules/              # Semgrep rules for different languages/frameworks
├── sample_project_python/       # Example projects
├── sample_project_java/
├── requirements.txt
├── README.md
└── ...
```

- **src/**: Core, reusable analyzer and reasoning code (imported by scripts in `analysis/`)
- **analysis/**: All runnable scripts for scanning, merging, reporting, and visualization
- **semgrep_rules/**: Semgrep rules for static analysis

## Features

- Extract feature flag usage points (multi-language, multi-style)
- Cross-file/module dependency analysis, cycle/conflict detection
- Interactive HTML and Graphviz dependency graph visualization
- Extensible Semgrep rules for different flag frameworks
- Modular, extensible, and patentable AST-based analysis

## Quick Start

### 1. Install Dependencies

```sh
pip install -r requirements.txt
```

### 2. One-step Full Demo (Recommended)

To run the full pipeline (Semgrep + AST + merge + report + visualize) in one command:

```sh
python3 analysis/demos/full_demo.py
```

### 3. Manual Step-by-step (Advanced)

#### a. Run Semgrep-based Analysis

```sh
python3 analysis/semgrep_based/semgrep_runner.py sample_project_python semgrep_rules/python-feature-flags.yml semgrep_auto_scan_result.json
```

#### b. Run AST-based Analysis

```sh
PYTHONPATH=src python3 analysis/ast_based/ast_runner.py sample_project_python python ast_auto_scan_result.json
```

#### c. Merge and Report

- Merge and deduplicate results:
  ```sh
  python3 analysis/ast_based/merge_flag_results.py
  ```
- Generate conflict/complexity report:
  ```sh
  python3 analysis/ast_based/flag_dependency_conflict_report.py
  ```
- Visualize the dependency graph:
  ```sh
  python3 analysis/ast_based/visualize_flag_graph.py
  ```

### 4. Example: Static Reasoning Demo

You can run a reasoning demo directly:
```sh
python3 src/feature_flag/reasoning.py
```

## Rule Extension & Adaptation

- Edit `semgrep_rules/*.yml` to match your flag framework and invocation style.
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

- Scan results output all flag usage points (file, line, invocation style).
- Combine with AST-based analysis and reporting for a full dependency/conflict graph.
- Use the visualization scripts for HTML or Graphviz output.

## Data Flow Analysis (NEW)

This project now includes a semantic Data Flow Analysis (DFA) engine for feature flag dependency/conflict detection:
- Tracks how feature flag values propagate through assignments, function calls, and returns.
- Detects when feature flag values reach sensitive operations (e.g., print, log, DB, network).
- Supports cross-function and return-value taint tracking.
- Results are clearly marked as `source: 'dataflow_analysis'` in merged outputs.

### How to Use

The full pipeline (including DFA) can be run with:

```sh
python3 analysis/demos/full_demo.py
```

Or run DFA alone:

```sh
PYTHONPATH=src python3 analysis/ast_based/dataflow_runner.py sample_project_python python dataflow_auto_scan_result.json
```

### Result Marking

- Each finding in `merged_flag_dependencies.json` is marked with its source:
  - `source: 'semgrep'` (pattern-based)
  - `source: 'ast'` (AST-based)
  - `source: 'dataflow_analysis'` (semantic data flow analysis)
- This allows you to trace which engine found each dependency or conflict.

---

For more details, see comments in each script and module. Contributions and extensions are welcome!
