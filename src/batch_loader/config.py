"""
YAML config loading and validation.

YOUR TASK: Implement the functions marked with TODO.

This module is responsible for:
  1. Reading the YAML file from disk
  2. Parsing the 'pipeline' section into a PipelineConfig
  3. Parsing each entry in 'documents' into a PipelineDocument
  4. Validating that all required fields are present
  5. Collecting and reporting validation errors (not failing on first error)

HINTS:
  - Use yaml.safe_load() (never yaml.load() — it's a security risk)
  - The YAML structure has two top-level keys: 'pipeline' and 'documents'
  - Each document is a dict that maps directly to PipelineDocument fields
  - Validation should collect ALL errors, not stop at the first one

REAL-WORLD CONTEXT:
  In the Clarizen pipeline, this is equivalent to:
    get_clarizen_documents(project_id)
  which reads pipe_config_clarizen.yaml from GCS and returns
  a list of dicts with 'document' and 'source_folder' keys.
"""

import yaml
from pathlib import Path
from typing import List, Tuple

from batch_loader.models import PipelineDocument, PipelineConfig


# These are the fields that MUST exist in each document entry.
# If any are missing, validation should report an error.
REQUIRED_DOCUMENT_FIELDS = [
    "document",
    "source_folder",
    "dest_dataset",
    "dest_table",
]


class ConfigError:
    """Represents a single validation error."""

    def __init__(self, field: str, message: str, document_index: int = -1):
        self.field = field
        self.message = message
        self.document_index = document_index

    def __str__(self):
        if self.document_index >= 0:
            return f"[Document #{self.document_index}] {self.field}: {self.message}"
        return f"[Pipeline] {self.field}: {self.message}"

    def __repr__(self):
        return f"ConfigError({self})"


def load_yaml(filepath: str) -> dict:
    """Read a YAML file and return its contents as a dict.

    TODO: Implement this function.

    Requirements:
      - Use yaml.safe_load() to parse the file
      - Raise FileNotFoundError if the file doesn't exist
      - Raise ValueError if the file is empty or not valid YAML
      - Return the parsed dict

    Args:
        filepath: Path to the YAML file (string or Path)

    Returns:
        Parsed YAML content as a dict

    Example:
        >>> data = load_yaml("configs/pipeline_config.yaml")
        >>> data.keys()
        dict_keys(['pipeline', 'documents'])
    """
    # TODO: Implement this function
    # Step 1: Convert filepath to a Path object
    # Step 2: Check if the file exists — raise FileNotFoundError if not
    # Step 3: Read the file contents
    # Step 4: Parse with yaml.safe_load()
    # Step 5: Validate the result is a dict (not None, not a string)
    # Step 6: Return the parsed dict
    pass


def validate_document(doc_dict: dict, index: int) -> List[ConfigError]:
    """Validate a single document entry from the YAML.

    TODO: Implement this function.

    Requirements:
      - Check that all REQUIRED_DOCUMENT_FIELDS are present in doc_dict
      - Check that 'document' (name) is not an empty string
      - Check that 'source_folder' is not an empty string
      - Collect ALL errors (don't stop at the first one)
      - Return a list of ConfigError objects (empty list = valid)

    Args:
        doc_dict: A single document entry from the YAML (raw dict)
        index: The position of this document in the list (for error messages)

    Returns:
        List of ConfigError objects (empty = no errors)

    Example:
        >>> errors = validate_document({"document": "Timesheet"}, 0)
        >>> len(errors)  # Missing source_folder, dest_dataset, dest_table
        3
        >>> str(errors[0])
        "[Document #0] source_folder: Required field is missing"
    """
    # TODO: Implement this function
    # Step 1: Create an empty list to collect errors
    # Step 2: Loop through REQUIRED_DOCUMENT_FIELDS
    # Step 3: For each field, check if it exists in doc_dict
    # Step 4: If it exists, check if it's an empty string
    # Step 5: Return the collected errors
    pass


def parse_documents(raw_documents: list) -> Tuple[List[PipelineDocument], List[ConfigError]]:
    """Parse and validate the list of document entries from YAML.

    TODO: Implement this function.

    Requirements:
      - Iterate through raw_documents (list of dicts)
      - Validate each one using validate_document()
      - If valid, create a PipelineDocument from the dict
      - Collect errors from invalid entries (but continue processing others)
      - Return both the valid documents AND the errors

    Args:
        raw_documents: List of dicts from the YAML 'documents' key

    Returns:
        Tuple of (valid_documents, all_errors)

    Example:
        >>> docs, errors = parse_documents([
        ...     {"document": "Timesheet", "source_folder": "ts",
        ...      "dest_dataset": "raw", "dest_table": "ts"},
        ...     {"document": ""},  # invalid
        ... ])
        >>> len(docs)
        1
        >>> len(errors)
        3  # empty name + missing source_folder + missing dest_dataset + missing dest_table
    """
    # TODO: Implement this function
    # Step 1: Create empty lists for valid_documents and all_errors
    # Step 2: Enumerate through raw_documents (you need the index for errors)
    # Step 3: For each entry, call validate_document()
    # Step 4: If no errors, create a PipelineDocument using **doc_dict
    #         (dict unpacking — the keys match the dataclass fields)
    #         HINT: You may need to filter doc_dict to only include
    #         fields that PipelineDocument expects. Use a set intersection.
    # Step 5: If errors, extend all_errors
    # Step 6: Return (valid_documents, all_errors)
    pass


def load_pipeline_config(filepath: str) -> Tuple[PipelineConfig, List[ConfigError]]:
    """Load and validate a complete pipeline configuration from YAML.

    TODO: Implement this function.

    This is the main entry point. It:
      1. Loads the YAML file
      2. Extracts pipeline-level settings
      3. Parses and validates all documents
      4. Constructs a PipelineConfig with the validated documents
      5. Returns the config and any validation errors

    Args:
        filepath: Path to the YAML config file

    Returns:
        Tuple of (PipelineConfig, list_of_errors)

    Example:
        >>> config, errors = load_pipeline_config("configs/pipeline_config.yaml")
        >>> config.name
        'clarizen_ingestion'
        >>> config.enabled_count
        9
        >>> len(errors)
        0
    """
    # TODO: Implement this function
    # Step 1: Call load_yaml() to get the raw dict
    # Step 2: Extract the 'pipeline' section (dict)
    # Step 3: Extract the 'documents' section (list)
    # Step 4: Call parse_documents() on the documents list
    # Step 5: Create a PipelineConfig from the pipeline section
    #         Set its .documents to the valid documents from step 4
    # Step 6: Return (config, errors)
    #
    # HINT: The pipeline section keys map to PipelineConfig fields,
    # but you need to handle the 'documents' key separately since
    # it's parsed by parse_documents(), not passed directly.
    pass
