"""Tests for the data models (models.py).

These tests are already passing — they validate the COMPLETE models.py.
Run these first to confirm your environment is set up correctly:
    pytest tests/test_models.py -v
"""

import pytest
from batch_loader.models import PipelineDocument, PipelineConfig


class TestPipelineDocument:
    """Test PipelineDocument dataclass."""

    def test_create_basic_document(self):
        """Create a document with required fields only."""
        doc = PipelineDocument(
            document="Timesheet",
            source_folder="timesheet",
            dest_dataset="tag_clarizen_raw",
            dest_table="timesheet",
        )
        assert doc.document == "Timesheet"
        assert doc.enabled is True  # default
        assert doc.source_file_delimiter == ","  # default

    def test_create_full_document(self):
        """Create a document with all fields."""
        doc = PipelineDocument(
            document="Project",
            enabled=False,
            source_folder="project",
            source_directory="clarizen_raw",
            source_file_delimiter="|",
            dest_dataset="tag_clarizen_raw",
            dest_table="project",
            bq_schema_json="project_schema.json",
        )
        assert doc.document == "Project"
        assert doc.enabled is False
        assert doc.source_file_delimiter == "|"

    def test_whitespace_stripping(self):
        """Fields should be stripped of leading/trailing whitespace."""
        doc = PipelineDocument(
            document="  Timesheet  ",
            source_folder="  timesheet  ",
            dest_dataset="tag_clarizen_raw",
            dest_table="timesheet",
        )
        assert doc.document == "Timesheet"
        assert doc.source_folder == "timesheet"

    def test_gcs_path_with_directory(self):
        """gcs_path should combine directory and folder."""
        doc = PipelineDocument(
            document="Timesheet",
            source_folder="timesheet",
            source_directory="clarizen_raw",
            dest_dataset="tag_clarizen_raw",
            dest_table="timesheet",
        )
        assert doc.gcs_path == "clarizen_raw/timesheet"

    def test_gcs_path_without_directory(self):
        """gcs_path should return just folder if no directory."""
        doc = PipelineDocument(
            document="Timesheet",
            source_folder="timesheet",
            source_directory="",
            dest_dataset="tag_clarizen_raw",
            dest_table="timesheet",
        )
        assert doc.gcs_path == "timesheet"

    def test_bq_full_table(self):
        """bq_full_table should be dataset.table."""
        doc = PipelineDocument(
            document="Timesheet",
            source_folder="timesheet",
            dest_dataset="tag_clarizen_raw",
            dest_table="timesheet",
        )
        assert doc.bq_full_table == "tag_clarizen_raw.timesheet"

    def test_to_dict(self):
        """to_dict should return all fields plus computed properties."""
        doc = PipelineDocument(
            document="Timesheet",
            source_folder="timesheet",
            source_directory="clarizen_raw",
            dest_dataset="tag_clarizen_raw",
            dest_table="timesheet",
        )
        d = doc.to_dict()
        assert d["document"] == "Timesheet"
        assert d["gcs_path"] == "clarizen_raw/timesheet"
        assert d["bq_full_table"] == "tag_clarizen_raw.timesheet"
        assert "enabled" in d

    def test_delimiter_normalization_tab(self):
        """Tab delimiter strings should be converted to actual tab char."""
        doc = PipelineDocument(
            document="Test",
            source_folder="test",
            dest_dataset="raw",
            dest_table="test",
            source_file_delimiter="\\t",
        )
        assert doc.source_file_delimiter == "\t"


class TestPipelineConfig:
    """Test PipelineConfig dataclass."""

    def test_create_basic_config(self):
        """Create a config with just a name."""
        config = PipelineConfig(name="test_pipeline")
        assert config.name == "test_pipeline"
        assert config.default_batch_size == 5
        assert config.documents == []

    def test_config_with_documents(self):
        """Config should hold a list of documents."""
        docs = [
            PipelineDocument(document="A", source_folder="a",
                             dest_dataset="raw", dest_table="a"),
            PipelineDocument(document="B", source_folder="b",
                             dest_dataset="raw", dest_table="b", enabled=False),
        ]
        config = PipelineConfig(name="test", documents=docs)
        assert config.enabled_count == 1
        assert config.disabled_count == 1

    def test_config_empty_name_raises(self):
        """Empty pipeline name should raise ValueError."""
        with pytest.raises(ValueError, match="name cannot be empty"):
            PipelineConfig(name="")

    def test_config_invalid_batch_size_raises(self):
        """Batch size < 1 should raise ValueError."""
        with pytest.raises(ValueError, match="Batch size must be >= 1"):
            PipelineConfig(name="test", default_batch_size=0)

    def test_config_invalid_timeout_raises(self):
        """Timeout < 1 should raise ValueError."""
        with pytest.raises(ValueError, match="Timeout must be >= 1"):
            PipelineConfig(name="test", timeout_minutes=-5)

    def test_config_summary(self):
        """summary() should return a readable one-liner."""
        docs = [
            PipelineDocument(document="A", source_folder="a",
                             dest_dataset="raw", dest_table="a"),
        ]
        config = PipelineConfig(name="my_pipeline", documents=docs,
                                environment="prod", default_batch_size=3)
        summary = config.summary()
        assert "my_pipeline" in summary
        assert "1 enabled" in summary
        assert "Batch size: 3" in summary
        assert "prod" in summary
