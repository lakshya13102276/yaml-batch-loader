"""Tests for config loading (config.py).

These tests will FAIL until you implement the TODOs in config.py.
They serve as the specification for what your code should do.

Run with: pytest tests/test_config.py -v
"""

import pytest
from pathlib import Path
from batch_loader.config import (
    load_yaml,
    validate_document,
    parse_documents,
    load_pipeline_config,
    REQUIRED_DOCUMENT_FIELDS,
)


# Helper to get the configs directory
CONFIGS_DIR = Path(__file__).parent.parent / "configs"


class TestLoadYaml:
    """Test the YAML file loading function."""

    def test_load_valid_yaml(self):
        """Should load a valid YAML file and return a dict."""
        data = load_yaml(str(CONFIGS_DIR / "pipeline_config.yaml"))
        assert isinstance(data, dict)
        assert "pipeline" in data
        assert "documents" in data

    def test_load_nonexistent_file(self):
        """Should raise FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            load_yaml("nonexistent_file.yaml")

    def test_load_returns_dict_with_documents_list(self):
        """The 'documents' key should contain a list."""
        data = load_yaml(str(CONFIGS_DIR / "pipeline_config.yaml"))
        assert isinstance(data["documents"], list)
        assert len(data["documents"]) > 0

    def test_load_pipeline_section_has_name(self):
        """The 'pipeline' section should have a 'name' field."""
        data = load_yaml(str(CONFIGS_DIR / "pipeline_config.yaml"))
        assert "name" in data["pipeline"]
        assert data["pipeline"]["name"] == "clarizen_ingestion"


class TestValidateDocument:
    """Test individual document validation."""

    def test_valid_document(self):
        """A complete document should produce no errors."""
        doc = {
            "document": "Timesheet",
            "source_folder": "timesheet",
            "dest_dataset": "tag_clarizen_raw",
            "dest_table": "timesheet",
        }
        errors = validate_document(doc, 0)
        assert len(errors) == 0

    def test_missing_document_name(self):
        """Missing 'document' field should produce an error."""
        doc = {
            "source_folder": "timesheet",
            "dest_dataset": "tag_clarizen_raw",
            "dest_table": "timesheet",
        }
        errors = validate_document(doc, 0)
        assert len(errors) >= 1
        assert any("document" in str(e) for e in errors)

    def test_missing_multiple_fields(self):
        """Missing multiple fields should produce multiple errors."""
        doc = {"document": "Timesheet"}
        errors = validate_document(doc, 0)
        # Missing: source_folder, dest_dataset, dest_table
        assert len(errors) == 3

    def test_empty_document_name(self):
        """Empty string document name should produce an error."""
        doc = {
            "document": "",
            "source_folder": "timesheet",
            "dest_dataset": "tag_clarizen_raw",
            "dest_table": "timesheet",
        }
        errors = validate_document(doc, 0)
        assert len(errors) >= 1
        assert any("empty" in str(e).lower() or "document" in str(e) for e in errors)

    def test_error_includes_document_index(self):
        """Error messages should reference the document index."""
        doc = {}  # Missing everything
        errors = validate_document(doc, 3)
        assert all(e.document_index == 3 for e in errors)

    def test_all_fields_missing(self):
        """Completely empty dict should produce error for each required field."""
        errors = validate_document({}, 0)
        assert len(errors) == len(REQUIRED_DOCUMENT_FIELDS)


class TestParseDocuments:
    """Test parsing a list of document dicts into PipelineDocument objects."""

    def test_parse_valid_documents(self):
        """All valid documents should be parsed successfully."""
        raw = [
            {
                "document": "Timesheet",
                "enabled": True,
                "source_folder": "timesheet",
                "source_directory": "clarizen_raw",
                "source_file_delimiter": ",",
                "dest_dataset": "tag_clarizen_raw",
                "dest_table": "timesheet",
                "bq_schema_json": "ts.json",
            },
            {
                "document": "Project",
                "enabled": False,
                "source_folder": "project",
                "source_directory": "clarizen_raw",
                "source_file_delimiter": ",",
                "dest_dataset": "tag_clarizen_raw",
                "dest_table": "project",
                "bq_schema_json": "proj.json",
            },
        ]
        docs, errors = parse_documents(raw)
        assert len(docs) == 2
        assert len(errors) == 0
        assert docs[0].document == "Timesheet"
        assert docs[1].enabled is False

    def test_parse_mixed_valid_and_invalid(self):
        """Valid docs should be returned, invalid ones produce errors."""
        raw = [
            {
                "document": "Timesheet",
                "source_folder": "ts",
                "dest_dataset": "raw",
                "dest_table": "ts",
            },
            {
                "document": "",  # invalid: empty name
            },
        ]
        docs, errors = parse_documents(raw)
        assert len(docs) == 1
        assert len(errors) > 0

    def test_parse_empty_list(self):
        """Empty document list should return empty results."""
        docs, errors = parse_documents([])
        assert len(docs) == 0
        assert len(errors) == 0

    def test_parse_ignores_extra_fields(self):
        """Extra fields in YAML should be ignored, not cause errors."""
        raw = [
            {
                "document": "Timesheet",
                "source_folder": "ts",
                "dest_dataset": "raw",
                "dest_table": "ts",
                "some_extra_field": "should be ignored",
                "another_one": 42,
            },
        ]
        docs, errors = parse_documents(raw)
        assert len(docs) == 1
        assert len(errors) == 0


class TestLoadPipelineConfig:
    """Test the full config loading pipeline."""

    def test_load_clarizen_config(self):
        """Should load the Clarizen config successfully."""
        config, errors = load_pipeline_config(
            str(CONFIGS_DIR / "pipeline_config.yaml")
        )
        assert config.name == "clarizen_ingestion"
        assert config.default_batch_size == 5
        assert config.environment == "staging"
        assert len(config.documents) > 0
        assert len(errors) == 0

    def test_load_360_config(self):
        """Should load the 360 config successfully."""
        config, errors = load_pipeline_config(
            str(CONFIGS_DIR / "pipeline_360.yaml")
        )
        assert config.name == "360_dashboard"
        assert config.default_batch_size == 3
        assert len(errors) == 0

    def test_load_invalid_config_reports_errors(self):
        """Invalid config should return errors but still parse valid docs."""
        config, errors = load_pipeline_config(
            str(CONFIGS_DIR / "invalid_config.yaml")
        )
        assert len(errors) > 0
        # The one valid document (WorkItem) should still be parsed
        valid_names = [d.document for d in config.documents]
        assert "WorkItem" in valid_names

    def test_enabled_count(self):
        """Config should correctly count enabled documents."""
        config, _ = load_pipeline_config(
            str(CONFIGS_DIR / "pipeline_config.yaml")
        )
        # The config has 9 enabled and 3 disabled
        assert config.enabled_count == 9
        assert config.disabled_count == 3

    def test_nonexistent_config_raises(self):
        """Loading a nonexistent config should raise FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_pipeline_config("nonexistent.yaml")
