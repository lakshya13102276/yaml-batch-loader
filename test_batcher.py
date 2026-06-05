"""Tests for batch creation (batcher.py).

Run with: pytest tests/test_batcher.py -v
"""

import json
import pytest
from batch_loader.models import PipelineDocument
from batch_loader.batcher import (
    create_batches,
    get_batch_summary,
    batch_plan_to_json,
    validate_batch_plan,
)


def _make_doc(name: str) -> PipelineDocument:
    """Helper to create a test document quickly."""
    return PipelineDocument(
        document=name,
        source_folder=name.lower(),
        dest_dataset="raw",
        dest_table=name.lower(),
    )


class TestCreateBatches:

    def test_exact_fit(self):
        """10 docs with batch_size=5 → exactly 2 batches."""
        docs = [_make_doc(f"Doc{i}") for i in range(10)]
        batches = create_batches(docs, batch_size=5)
        assert len(batches) == 2
        assert len(batches[0]) == 5
        assert len(batches[1]) == 5

    def test_remainder(self):
        """12 docs with batch_size=5 → 3 batches, last has 2."""
        docs = [_make_doc(f"Doc{i}") for i in range(12)]
        batches = create_batches(docs, batch_size=5)
        assert len(batches) == 3
        assert len(batches[0]) == 5
        assert len(batches[1]) == 5
        assert len(batches[2]) == 2

    def test_single_batch(self):
        """3 docs with batch_size=5 → 1 batch with 3 docs."""
        docs = [_make_doc(f"Doc{i}") for i in range(3)]
        batches = create_batches(docs, batch_size=5)
        assert len(batches) == 1
        assert len(batches[0]) == 3

    def test_one_doc_per_batch(self):
        """batch_size=1 → each doc gets its own batch."""
        docs = [_make_doc(f"Doc{i}") for i in range(4)]
        batches = create_batches(docs, batch_size=1)
        assert len(batches) == 4
        for batch_docs in batches.values():
            assert len(batch_docs) == 1

    def test_empty_list(self):
        """Empty input → empty output."""
        batches = create_batches([], batch_size=5)
        assert len(batches) == 0

    def test_single_document(self):
        """One doc → one batch with one doc."""
        docs = [_make_doc("Only")]
        batches = create_batches(docs, batch_size=5)
        assert len(batches) == 1
        assert batches[0][0].document == "Only"

    def test_preserves_order(self):
        """Documents should appear in batches in their original order."""
        names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"]
        docs = [_make_doc(n) for n in names]
        batches = create_batches(docs, batch_size=2)
        assert batches[0][0].document == "Alpha"
        assert batches[0][1].document == "Beta"
        assert batches[1][0].document == "Gamma"
        assert batches[1][1].document == "Delta"
        assert batches[2][0].document == "Epsilon"

    def test_batch_numbers_are_sequential(self):
        """Batch keys should be 0, 1, 2, ... with no gaps."""
        docs = [_make_doc(f"Doc{i}") for i in range(7)]
        batches = create_batches(docs, batch_size=3)
        assert list(batches.keys()) == [0, 1, 2]

    def test_default_batch_size_is_five(self):
        """Default batch size should be 5 (matching Clarizen pipeline)."""
        docs = [_make_doc(f"Doc{i}") for i in range(11)]
        batches = create_batches(docs)  # no batch_size argument
        assert len(batches[0]) == 5


class TestGetBatchSummary:

    def test_summary_contains_batch_numbers(self):
        docs = [_make_doc(f"Doc{i}") for i in range(7)]
        batches = create_batches(docs, batch_size=3)
        summary = get_batch_summary(batches)
        assert "Batch" in summary or "batch" in summary
        assert "Doc0" in summary

    def test_summary_contains_totals(self):
        docs = [_make_doc(f"Doc{i}") for i in range(7)]
        batches = create_batches(docs, batch_size=3)
        summary = get_batch_summary(batches)
        assert "7" in summary  # total docs
        assert "3" in summary  # total batches

    def test_summary_empty_batches(self):
        summary = get_batch_summary({})
        assert "0" in summary  # should show zero


class TestBatchPlanToJson:

    def test_json_is_valid(self):
        docs = [_make_doc(f"Doc{i}") for i in range(3)]
        batches = create_batches(docs, batch_size=2)
        result = batch_plan_to_json(batches, "test_pipeline")
        parsed = json.loads(result)
        assert parsed["pipeline"] == "test_pipeline"
        assert parsed["total_batches"] == 2
        assert parsed["total_documents"] == 3

    def test_json_batch_structure(self):
        docs = [_make_doc("Timesheet"), _make_doc("Project")]
        batches = create_batches(docs, batch_size=5)
        result = batch_plan_to_json(batches, "test")
        parsed = json.loads(result)
        batch_0 = parsed["batches"][0]
        assert batch_0["batch_number"] == 0
        assert batch_0["document_count"] == 2

    def test_json_includes_throttle(self):
        docs = [_make_doc("A")]
        batches = create_batches(docs)
        result = batch_plan_to_json(batches, "test", throttle_seconds=30)
        parsed = json.loads(result)
        assert parsed["throttle_seconds"] == 30


class TestValidateBatchPlan:

    def test_valid_plan_no_warnings(self):
        docs = [_make_doc(f"Doc{i}") for i in range(5)]
        batches = create_batches(docs, batch_size=3)
        warnings = validate_batch_plan(batches)
        assert len(warnings) == 0

    def test_empty_plan_no_warnings(self):
        warnings = validate_batch_plan({})
        assert len(warnings) == 0
