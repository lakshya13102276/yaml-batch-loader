"""Tests for document filtering (filter.py).

Run with: pytest tests/test_filter.py -v
"""

import pytest
from batch_loader.models import PipelineDocument
from batch_loader.filter import (
    get_enabled_documents,
    deduplicate_documents,
    filter_by_field,
    get_document_summary,
)


def _make_doc(name: str, enabled: bool = True, dataset: str = "raw",
              table: str = None) -> PipelineDocument:
    """Helper to create a test document quickly."""
    return PipelineDocument(
        document=name,
        enabled=enabled,
        source_folder=name.lower().replace(" ", "_"),
        dest_dataset=dataset,
        dest_table=table or name.lower().replace(" ", "_"),
    )


class TestGetEnabledDocuments:

    def test_all_enabled(self):
        docs = [_make_doc("A"), _make_doc("B"), _make_doc("C")]
        result = get_enabled_documents(docs)
        assert len(result) == 3

    def test_some_disabled(self):
        docs = [_make_doc("A"), _make_doc("B", enabled=False), _make_doc("C")]
        result = get_enabled_documents(docs)
        assert len(result) == 2
        assert result[0].document == "A"
        assert result[1].document == "C"

    def test_all_disabled(self):
        docs = [_make_doc("A", enabled=False), _make_doc("B", enabled=False)]
        result = get_enabled_documents(docs)
        assert len(result) == 0

    def test_empty_list(self):
        result = get_enabled_documents([])
        assert len(result) == 0

    def test_preserves_order(self):
        docs = [_make_doc("C"), _make_doc("A", enabled=False), _make_doc("B")]
        result = get_enabled_documents(docs)
        assert [d.document for d in result] == ["C", "B"]


class TestDeduplicateDocuments:

    def test_no_duplicates(self):
        docs = [_make_doc("A"), _make_doc("B"), _make_doc("C")]
        result = deduplicate_documents(docs)
        assert len(result) == 3

    def test_duplicate_keeps_first(self):
        docs = [
            _make_doc("A", table="a_v1"),
            _make_doc("A", table="a_v2"),
            _make_doc("B"),
        ]
        result = deduplicate_documents(docs, key="document", strategy="first")
        assert len(result) == 2
        assert result[0].dest_table == "a_v1"  # kept first

    def test_duplicate_keeps_last(self):
        docs = [
            _make_doc("A", table="a_v1"),
            _make_doc("A", table="a_v2"),
            _make_doc("B"),
        ]
        result = deduplicate_documents(docs, key="document", strategy="last")
        assert len(result) == 2
        # The "A" entry should be the second one (a_v2)
        a_doc = [d for d in result if d.document == "A"][0]
        assert a_doc.dest_table == "a_v2"

    def test_dedup_by_dest_table(self):
        docs = [
            _make_doc("A", table="shared_table"),
            _make_doc("B", table="shared_table"),
            _make_doc("C", table="other_table"),
        ]
        result = deduplicate_documents(docs, key="dest_table", strategy="first")
        assert len(result) == 2

    def test_empty_list(self):
        result = deduplicate_documents([])
        assert len(result) == 0


class TestFilterByField:

    def test_filter_by_dataset(self):
        docs = [
            _make_doc("A", dataset="raw"),
            _make_doc("B", dataset="dwh_360"),
            _make_doc("C", dataset="raw"),
        ]
        result = filter_by_field(docs, "dest_dataset", "raw")
        assert len(result) == 2

    def test_filter_case_insensitive(self):
        docs = [_make_doc("A", dataset="RAW"), _make_doc("B", dataset="raw")]
        result = filter_by_field(docs, "dest_dataset", "raw")
        assert len(result) == 2

    def test_filter_no_matches(self):
        docs = [_make_doc("A", dataset="raw")]
        result = filter_by_field(docs, "dest_dataset", "nonexistent")
        assert len(result) == 0

    def test_filter_invalid_field_raises(self):
        docs = [_make_doc("A")]
        with pytest.raises(AttributeError):
            filter_by_field(docs, "nonexistent_field", "value")


class TestGetDocumentSummary:

    def test_summary_counts(self):
        docs = [
            _make_doc("A", enabled=True, dataset="raw"),
            _make_doc("B", enabled=False, dataset="raw"),
            _make_doc("C", enabled=True, dataset="dwh"),
        ]
        summary = get_document_summary(docs)
        assert summary["total"] == 3
        assert summary["enabled"] == 2
        assert summary["disabled"] == 1

    def test_summary_by_dataset(self):
        docs = [
            _make_doc("A", dataset="raw"),
            _make_doc("B", dataset="dwh"),
            _make_doc("C", dataset="raw"),
        ]
        summary = get_document_summary(docs)
        assert summary["by_dataset"]["raw"] == 2
        assert summary["by_dataset"]["dwh"] == 1

    def test_summary_document_lists(self):
        docs = [
            _make_doc("A", enabled=True),
            _make_doc("B", enabled=False),
        ]
        summary = get_document_summary(docs)
        assert "A" in summary["documents_enabled"]
        assert "B" in summary["documents_disabled"]

    def test_empty_list(self):
        summary = get_document_summary([])
        assert summary["total"] == 0
