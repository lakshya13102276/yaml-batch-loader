"""
Document filtering logic.

YOUR TASK: Implement the functions marked with TODO.

This module handles:
  1. Filtering to only enabled documents
  2. Deduplicating documents by name (in case of config errors)
  3. Filtering by specific field values (e.g., only docs for a certain dataset)

REAL-WORLD CONTEXT:
  In the Clarizen pipeline, get_clarizen_documents() returns only enabled
  documents. But in practice, you often need more sophisticated filtering:
  - "Only process documents for the tag_clarizen_raw dataset"
  - "Only process documents that have changed since last run"
  - "Skip documents that failed in the previous batch"

  This module builds the pattern for all of those.
"""

from typing import List, Dict, Optional, Callable
from collections import defaultdict

from batch_loader.models import PipelineDocument


def get_enabled_documents(documents: List[PipelineDocument]) -> List[PipelineDocument]:
    """Filter to only enabled documents.

    TODO: Implement this function.

    This is the simplest filter — return only documents where enabled is True.
    Preserve the original order.

    Args:
        documents: Full list of PipelineDocument objects

    Returns:
        Filtered list containing only enabled documents

    Example:
        >>> docs = [
        ...     PipelineDocument(document="A", enabled=True, ...),
        ...     PipelineDocument(document="B", enabled=False, ...),
        ...     PipelineDocument(document="C", enabled=True, ...),
        ... ]
        >>> result = get_enabled_documents(docs)
        >>> [d.document for d in result]
        ['A', 'C']
    """
    # TODO: Implement using a list comprehension
    # This is a one-liner, but think about what it represents:
    # In production, this is the gate that controls which Dataflow jobs run.
    pass


def deduplicate_documents(
    documents: List[PipelineDocument],
    key: str = "document",
    strategy: str = "first"
) -> List[PipelineDocument]:
    """Remove duplicate documents based on a key field.

    TODO: Implement this function.

    Sometimes configs have duplicate entries (copy-paste errors, merge conflicts).
    This function removes duplicates while preserving order.

    Args:
        documents: List of PipelineDocument objects (may have duplicates)
        key: Which field to deduplicate on ("document", "dest_table", etc.)
        strategy: "first" keeps the first occurrence, "last" keeps the last

    Returns:
        Deduplicated list of documents

    Example:
        >>> docs = [
        ...     PipelineDocument(document="Timesheet", dest_table="ts_v1", ...),
        ...     PipelineDocument(document="Timesheet", dest_table="ts_v2", ...),
        ...     PipelineDocument(document="Project", dest_table="proj", ...),
        ... ]
        >>> result = deduplicate_documents(docs, key="document", strategy="first")
        >>> [d.dest_table for d in result]
        ['ts_v1', 'proj']  # kept first Timesheet, skipped second
    """
    # TODO: Implement this function
    # Step 1: Create a dict to track seen keys (use a dict, not a set,
    #         because you need to track the index for "last" strategy)
    # Step 2: Iterate through documents
    # Step 3: For each document, get the value of the key field using getattr()
    # Step 4: Based on strategy, decide whether to keep or skip
    # Step 5: Return the deduplicated list
    #
    # HINT for "last" strategy: One approach is to iterate in reverse,
    # use "first" logic, then reverse the result.
    # Another approach: build a dict of key -> document (last write wins),
    # then filter the original list to only include kept entries.
    pass


def filter_by_field(
    documents: List[PipelineDocument],
    field_name: str,
    field_value: str
) -> List[PipelineDocument]:
    """Filter documents where a specific field matches a value.

    TODO: Implement this function.

    Useful for commands like:
      --filter-by dest_dataset=tag_clarizen_raw
      --filter-by source_directory=clarizen_raw

    Args:
        documents: List of PipelineDocument objects
        field_name: Name of the field to filter on
        field_value: Value to match (case-insensitive)

    Returns:
        Filtered list of documents

    Raises:
        AttributeError: If field_name doesn't exist on PipelineDocument

    Example:
        >>> result = filter_by_field(docs, "dest_dataset", "dwh_360")
        >>> [d.document for d in result]
        ['AccountHierarchy', 'ServiceContractRevenue']
    """
    # TODO: Implement this function
    # Step 1: Validate that field_name exists on PipelineDocument
    #         HINT: Use hasattr() on the first document, or check against
    #         PipelineDocument.__dataclass_fields__
    # Step 2: Filter using getattr() and case-insensitive comparison
    pass


def get_document_summary(documents: List[PipelineDocument]) -> Dict:
    """Generate a summary of the document list.

    TODO: Implement this function.

    Returns a dict with useful statistics about the document list.

    Returns:
        {
            "total": 12,
            "enabled": 9,
            "disabled": 3,
            "by_dataset": {"tag_clarizen_raw": 9, "dwh_360": 3},
            "by_directory": {"clarizen_raw": 12},
            "documents_enabled": ["Timesheet", "Project", ...],
            "documents_disabled": ["Issue", "Risk", ...],
        }
    """
    # TODO: Implement this function
    # HINT: Use defaultdict(int) for the counting dicts
    # HINT: Use defaultdict(list) if you want to group documents by dataset
    pass
