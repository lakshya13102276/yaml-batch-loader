"""
Data models for the pipeline configuration.

THIS FILE IS COMPLETE — no TODOs. Study it to understand:
  - How dataclasses replace raw dicts for type safety
  - How __post_init__ enables validation at creation time
  - How default_factory works for mutable defaults
  - How to add computed properties to dataclasses

In the real Clarizen pipeline, documents are plain dicts:
    {'document': 'Timesheet', 'source_folder': 'timesheet'}

Dataclasses give you the same thing but with:
  - Autocompletion in your IDE
  - Type checking
  - Built-in __repr__ for debugging
  - Validation in __post_init__
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PipelineDocument:
    """Represents one document/table entry from the YAML config.

    Maps to a single entry in the 'documents' list in the YAML.
    In production, each PipelineDocument becomes one unit of work
    inside a Dataflow job batch.

    Example YAML entry:
        - document: Timesheet
          enabled: true
          source_folder: timesheet
          source_directory: clarizen_raw
          source_file_delimiter: ","
          dest_dataset: tag_clarizen_raw
          dest_table: timesheet
          bq_schema_json: timesheet_schema.json
    """

    # Required fields — must be provided
    document: str                   # Human-readable name (e.g., "Timesheet")
    source_folder: str              # GCS folder containing source files
    dest_dataset: str               # BigQuery dataset to write to
    dest_table: str                 # BigQuery table name

    # Optional fields with defaults
    enabled: bool = True            # Whether to include in processing
    source_directory: str = ""      # Parent directory in GCS
    source_file_delimiter: str = ","  # CSV delimiter (comma, pipe, tab)
    bq_schema_json: str = ""        # Path to the BQ schema JSON file

    def __post_init__(self):
        """Validate fields after dataclass initialization.

        This runs automatically when you create a PipelineDocument.
        It's the dataclass equivalent of validation in a constructor.
        """
        # Strip whitespace from string fields
        self.document = self.document.strip()
        self.source_folder = self.source_folder.strip()
        self.dest_dataset = self.dest_dataset.strip()
        self.dest_table = self.dest_table.strip()

        # Normalize delimiter (handle escaped characters)
        delimiter_map = {"\\t": "\t", "\\|": "|", "tab": "\t", "pipe": "|"}
        if self.source_file_delimiter in delimiter_map:
            self.source_file_delimiter = delimiter_map[self.source_file_delimiter]

    @property
    def gcs_path(self) -> str:
        """Compute the full GCS source path.

        Returns something like: clarizen_raw/timesheet
        In production this would be: gs://{bucket}/clarizen_raw/timesheet
        """
        if self.source_directory:
            return f"{self.source_directory}/{self.source_folder}"
        return self.source_folder

    @property
    def bq_full_table(self) -> str:
        """Compute the fully qualified BigQuery table reference.

        Returns something like: tag_clarizen_raw.timesheet
        In production: project_id.tag_clarizen_raw.timesheet
        """
        return f"{self.dest_dataset}.{self.dest_table}"

    def to_dict(self) -> dict:
        """Convert to a plain dict (useful for JSON serialization)."""
        return {
            "document": self.document,
            "enabled": self.enabled,
            "source_folder": self.source_folder,
            "source_directory": self.source_directory,
            "source_file_delimiter": self.source_file_delimiter,
            "dest_dataset": self.dest_dataset,
            "dest_table": self.dest_table,
            "bq_schema_json": self.bq_schema_json,
            "gcs_path": self.gcs_path,
            "bq_full_table": self.bq_full_table,
        }


@dataclass
class PipelineConfig:
    """Top-level pipeline configuration parsed from YAML.

    Contains both pipeline-level settings (name, schedule, batch size)
    and the list of documents to process.

    In the real Clarizen pipeline, some of these settings come from
    Airflow variables or DAG defaults rather than the YAML — but the
    concept is the same: config drives behavior.
    """

    name: str
    owner: str = "Data Warehouse Analytics"
    schedule: str = "manual"
    timeout_minutes: int = 1800
    default_batch_size: int = 5
    throttle_seconds: int = 20
    environment: str = "dev"
    documents: List[PipelineDocument] = field(default_factory=list)

    def __post_init__(self):
        """Validate pipeline-level settings."""
        if not self.name:
            raise ValueError("Pipeline name cannot be empty")
        if self.default_batch_size < 1:
            raise ValueError(f"Batch size must be >= 1, got {self.default_batch_size}")
        if self.timeout_minutes < 1:
            raise ValueError(f"Timeout must be >= 1, got {self.timeout_minutes}")

    @property
    def enabled_count(self) -> int:
        """Count of enabled documents."""
        return sum(1 for d in self.documents if d.enabled)

    @property
    def disabled_count(self) -> int:
        """Count of disabled documents."""
        return sum(1 for d in self.documents if not d.enabled)

    def summary(self) -> str:
        """One-line summary of the config."""
        return (
            f"Pipeline '{self.name}' | "
            f"{self.enabled_count} enabled, {self.disabled_count} disabled | "
            f"Batch size: {self.default_batch_size} | "
            f"Env: {self.environment}"
        )
