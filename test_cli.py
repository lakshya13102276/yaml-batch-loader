"""Tests for the CLI (cli.py).

Run with: pytest tests/test_cli.py -v

These tests call main() with argv directly rather than subprocess,
so they test the logic without needing a real terminal.
"""

import pytest
from pathlib import Path
from batch_loader.cli import main

CONFIGS_DIR = str(Path(__file__).parent.parent / "configs")


class TestCLI:

    def test_basic_run(self):
        """Basic run with valid config should return 0."""
        result = main(["--config", f"{CONFIGS_DIR}/pipeline_config.yaml"])
        assert result == 0

    def test_custom_batch_size(self):
        """Custom batch size should not cause errors."""
        result = main([
            "--config", f"{CONFIGS_DIR}/pipeline_config.yaml",
            "--batch-size", "3",
        ])
        assert result == 0

    def test_dry_run(self):
        """Dry run should succeed."""
        result = main([
            "--config", f"{CONFIGS_DIR}/pipeline_config.yaml",
            "--dry-run",
        ])
        assert result == 0

    def test_json_format(self):
        """JSON output format should succeed."""
        result = main([
            "--config", f"{CONFIGS_DIR}/pipeline_config.yaml",
            "--format", "json",
        ])
        assert result == 0

    def test_validate_only(self):
        """Validate-only mode should succeed for valid config."""
        result = main([
            "--config", f"{CONFIGS_DIR}/pipeline_config.yaml",
            "--validate-only",
        ])
        assert result == 0

    def test_invalid_config_reports_errors(self):
        """Invalid config should return non-zero or print warnings."""
        result = main([
            "--config", f"{CONFIGS_DIR}/invalid_config.yaml",
        ])
        # Should still run (valid docs are processed) but may return 1
        # if you choose to make validation errors a non-zero exit
        assert result in (0, 1)

    def test_nonexistent_config_fails(self):
        """Missing config file should fail."""
        with pytest.raises((FileNotFoundError, SystemExit)):
            main(["--config", "nonexistent.yaml"])

    def test_360_config(self):
        """Should work with the 360 pipeline config too."""
        result = main(["--config", f"{CONFIGS_DIR}/pipeline_360.yaml"])
        assert result == 0
