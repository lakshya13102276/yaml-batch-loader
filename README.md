# YAML-Driven Batch Config Loader

A production-style Python project that mirrors the config-driven batch processing pattern used in the data pipeline. Built as a learning exercise for data engineers working with GCP/Airflow/Dataflow pipelines.

## What This Project Teaches You

This project recreates the exact pattern from `pipe_config_clarizen.yaml` → `get_clarizen_documents()` → batch grouping → sequential Dataflow job execution. By building it yourself, you internalize:

- **YAML config parsing** — how pipeline behavior is driven by config, not code changes
- **Dataclass validation** — how to model pipeline entities with type safety
- **Dictionary patterns** — grouping, filtering, lookups (the #1 pattern in DE work)
- **Batch partitioning** — splitting N items into groups of K (how Clarizen processes 5 docs per Dataflow job)
- **CLI design** — how to make your tools usable by other engineers
- **Testing** — how to verify pipeline logic before it touches real infrastructure

## Architecture Overview

```
┌─────────────────────────────────────┐
│         YAML Config File            │
│   (configs/pipeline_config.yaml)    │
│                                     │
│  documents:                         │
│    - document: Timesheet            │
│      enabled: true                  │
│      source_folder: timesheet       │
│      ...                            │
└──────────────┬──────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│          Config Loader               │
│   (src/batch_loader/config.py)       │
│                                      │
│  • Reads YAML from disk              │
│  • Validates required fields         │
│  • Returns List[PipelineDocument]    │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│          Document Filter             │
│   (src/batch_loader/filter.py)       │
│                                      │
│  • Filters to enabled == True        │
│  • Validates source paths exist      │
│  • Deduplicates by document name     │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│          Batch Creator               │
│   (src/batch_loader/batcher.py)      │
│                                      │
│  • Groups docs into batches of N     │
│  • Returns Dict[int, List[Doc]]      │
│  • Generates execution summary       │
└──────────────┬───────────────────────┘
               │
               ▼
┌──────────────────────────────────────┐
│          CLI Interface               │
│   (src/batch_loader/cli.py)          │
│                                      │
│  • --config: path to YAML            │
│  • --batch-size: docs per batch      │
│  • --dry-run: preview without exec   │
│  • --format: output as table/json    │
└──────────────────────────────────────┘
```

## Project Structure

```
yaml-batch-loader/
├── .devcontainer/
│   └── devcontainer.json        ← GitHub Codespace config
├── .github/
│   └── workflows/
│       └── ci.yml               ← Auto-run tests on push
├── configs/
│   ├── pipeline_config.yaml     ← Main config (mirrors Clarizen)
│   ├── pipeline_360.yaml        ← Second config (mirrors 360 pipeline)
│   └── invalid_config.yaml      ← Intentionally broken for testing
├── src/
│   └── batch_loader/
│       ├── __init__.py
│       ├── models.py            ← Dataclass definitions
│       ├── config.py            ← YAML loading + validation
│       ├── filter.py            ← Document filtering logic
│       ├── batcher.py           ← Batch grouping logic
│       └── cli.py               ← Command-line interface
├── tests/
│   ├── __init__.py
│   ├── test_models.py           ← Test dataclass creation
│   ├── test_config.py           ← Test YAML loading
│   ├── test_filter.py           ← Test filtering logic
│   ├── test_batcher.py          ← Test batch grouping
│   └── test_cli.py              ← Test CLI end-to-end
├── requirements.txt
├── pyproject.toml
└── README.md
```

## How to Develop (GitHub Codespaces)

1. Push this repo to GitHub
2. Click **Code → Codespaces → Create codespace on main**
3. Wait for the container to build (~30 seconds)
4. Terminal opens with Python 3.11 + all dependencies ready

### Run the CLI
```bash
# Basic run
python -m batch_loader --config configs/pipeline_config.yaml

# Custom batch size
python -m batch_loader --config configs/pipeline_config.yaml --batch-size 3

# Dry run with JSON output
python -m batch_loader --config configs/pipeline_config.yaml --dry-run --format json

# Validate config without processing
python -m batch_loader --config configs/pipeline_config.yaml --validate-only
```

### Run Tests
```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_batcher.py -v

# With coverage
pytest tests/ -v --cov=src/batch_loader --cov-report=term-missing
```

## Exercises (Ordered by Difficulty)

### Level 1 — Read and understand (do these first)
- [ ] Read `configs/pipeline_config.yaml` — understand every field
- [ ] Read `src/batch_loader/models.py` — understand the dataclass
- [ ] Run `python -m batch_loader --config configs/pipeline_config.yaml` and read the output

### Level 2 — Fill in the TODOs
- [ ] Complete `config.py` → `load_pipeline_config()` 
- [ ] Complete `config.py` → `validate_document()` 
- [ ] Complete `filter.py` → `get_enabled_documents()`
- [ ] Complete `filter.py` → `deduplicate_documents()`
- [ ] Complete `batcher.py` → `create_batches()`
- [ ] Complete `batcher.py` → `get_batch_summary()`

### Level 3 — Make all tests pass
- [ ] Run `pytest tests/ -v` and fix until green
- [ ] Add edge case tests you think are missing

### Level 4 — Extend the project
- [ ] Add a `--filter-by` flag to the CLI (e.g., `--filter-by dataset=tag_clarizen_raw`)
- [ ] Add config inheritance: a base config + environment overrides
- [ ] Add a `--output` flag that writes the batch plan to a JSON file
- [ ] Add schema validation using `jsonschema` or `pydantic`

## How This Maps to Real Work

| This Project | Real Clarizen Pipeline |
|---|---|
| `pipeline_config.yaml` | `pipe_config_clarizen.yaml` in GCS |
| `load_pipeline_config()` | `get_clarizen_documents(project_id)` |
| `PipelineDocument` dataclass | Dict with 'document' and 'source_folder' keys |
| `create_batches(docs, 5)` | Grouping 5 docs per Dataflow job |
| `--dry-run` flag | Testing config changes before deploying to Composer |
| `pytest` tests | Unit tests before promoting DAG to production |
