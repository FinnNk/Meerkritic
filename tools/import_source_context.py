"""Attach preserved GitHub evidence explicitly; never fetch sources or run models."""

import argparse
import sys
from pathlib import Path


def main() -> None:
    """Import bounded raw response and receipt files for one unreviewed terminal job."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--response", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from semantic_reviewer.adapters.reading import MAX_RECEIPT_BYTES, GitHubReadingSources
    from semantic_reviewer.bootstrap import build_jobs, runtime_path

    root = runtime_path(args.data_root)
    jobs = build_jobs(root)
    job, _ = jobs.inspect(args.job)
    _, source = jobs.datasets.observation(job.dataset_id, job.source_index)
    with args.response.open("rb") as stream:
        response = stream.read(MAX_RECEIPT_BYTES + 1)
    with args.receipt.open("rb") as stream:
        receipt = stream.read(MAX_RECEIPT_BYTES + 1)
    context = GitHubReadingSources(root / "source-context", root / "state.sqlite3").attach(
        job, source, response, receipt
    )
    print(context.sha256)


if __name__ == "__main__":
    main()
