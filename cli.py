"""
Command-line interface for the batch config loader.

YOUR TASK: Implement the main() function marked with TODO.

Usage:
    python -m batch_loader --config configs/pipeline_config.yaml
    python -m batch_loader --config configs/pipeline_config.yaml --batch-size 3
    python -m batch_loader --config configs/pipeline_config.yaml --dry-run
    python -m batch_loader --config configs/pipeline_config.yaml --format json
    python -m batch_loader --config configs/pipeline_config.yaml --validate-only

REAL-WORLD CONTEXT:
  In the Clarizen pipeline, you don't have a CLI — Airflow reads the config
  directly. But having a CLI is essential for:
  - Testing config changes before deploying to Composer
  - Debugging: "why did batch 2 include this document?"
  - CI/CD: validating configs in a GitHub Action before merge
  - Onboarding: new team members can see what a config does without
    reading the DAG code
"""

import argparse
import sys
import json
from typing import List

from batch_loader.config import load_pipeline_config
from batch_loader.filter import get_enabled_documents, deduplicate_documents, filter_by_field
from batch_loader.batcher import create_batches, get_batch_summary, batch_plan_to_json


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    This is already complete — study it to understand argparse patterns.
    """
    parser = argparse.ArgumentParser(
        prog="batch-loader",
        description="YAML-Driven Batch Config Loader for Data Pipelines",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --config configs/pipeline_config.yaml
  %(prog)s --config configs/pipeline_config.yaml --batch-size 3
  %(prog)s --config configs/pipeline_config.yaml --dry-run --format json
  %(prog)s --config configs/pipeline_config.yaml --validate-only
  %(prog)s --config configs/pipeline_config.yaml --filter-by dest_dataset=dwh_360
        """,
    )

    parser.add_argument(
        "--config", "-c",
        required=True,
        help="Path to the YAML pipeline config file",
    )

    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=None,  # None means "use the config's default"
        help="Number of documents per batch (overrides config value)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview the batch plan without executing",
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the config, don't create batch plan",
    )

    parser.add_argument(
        "--format", "-f",
        choices=["table", "json"],
        default="table",
        help="Output format (default: table)",
    )

    parser.add_argument(
        "--filter-by",
        type=str,
        default=None,
        help="Filter documents by field=value (e.g., dest_dataset=dwh_360)",
    )

    parser.add_argument(
        "--include-disabled",
        action="store_true",
        help="Include disabled documents in the output",
    )

    return parser


def main(argv: List[str] = None) -> int:
    """Main entry point for the CLI.

    TODO: Implement this function.

    The flow should be:
      1. Parse command-line arguments
      2. Load and validate the config
      3. Report any validation errors
      4. If --validate-only, stop here
      5. Filter documents (enabled only, unless --include-disabled)
      6. Apply --filter-by if provided
      7. Deduplicate
      8. Create batches
      9. Output the result in the requested format

    Args:
        argv: Command-line arguments (None = use sys.argv)

    Returns:
        Exit code (0 = success, 1 = validation errors, 2 = runtime error)
    """
    # TODO: Implement this function
    #
    # Step 1: Parse arguments
    #   parser = build_parser()
    #   args = parser.parse_args(argv)
    #
    # Step 2: Load config
    #   config, errors = load_pipeline_config(args.config)
    #
    # Step 3: Report errors
    #   If there are errors, print them and return exit code 1
    #   But still continue with valid documents (warn, don't fail)
    #
    # Step 4: Handle --validate-only
    #   Print config.summary() and return 0
    #
    # Step 5: Filter documents
    #   Start with config.documents
    #   If not args.include_disabled: filter to enabled only
    #   If args.filter_by: parse "field=value" and apply filter_by_field()
    #
    # Step 6: Deduplicate
    #   docs = deduplicate_documents(docs)
    #
    # Step 7: Determine batch size
    #   batch_size = args.batch_size or config.default_batch_size
    #
    # Step 8: Create batches
    #   batches = create_batches(docs, batch_size)
    #
    # Step 9: Output
    #   If args.format == "json":
    #       print(batch_plan_to_json(batches, config.name))
    #   Else:
    #       print(get_batch_summary(batches))
    #
    # Step 10: If --dry-run, print a note saying "DRY RUN — no execution"
    #
    # Return 0
    pass


# This allows running with: python -m batch_loader
if __name__ == "__main__":
    sys.exit(main() or 0)
