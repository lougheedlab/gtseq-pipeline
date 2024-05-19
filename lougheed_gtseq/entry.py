import argparse
from pathlib import Path

from .models import Params
from .pipeline import run_pipeline


def main():
    parser = argparse.ArgumentParser(prog="lougheed_gtseq")
    parser.add_argument(
        "--species",
        type=str,
        help="Species/GTseq panel for the pipeline.",
        choices=("polar",),
    )
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path.cwd(),
        help="Working directory for reference genomes, alignments, etc.",
    )
    parser.add_argument(
        "--processes", "-p", type=int, help="Number of processes to use.", default=2
    )
    parser.add_argument(
        "run", type=Path, help="Path to run input directory (from Illumina machine)"
    )
    parser.add_argument("samples", type=Path, help="Path to sample sheet.")

    args = parser.parse_args()

    params = Params(
        species=args.species,
        work_dir=args.work_dir,
        run=args.run,
        samples=args.samples,
        processes=args.processes,
    )

    run_pipeline(params)


if __name__ == "__main__":
    main()
