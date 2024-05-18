import argparse
from pathlib import Path

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
    parser.add_argument("--processes", "-p", type=int, help="Number of processes to use.", default=2)
    parser.add_argument("run", type=Path, help="Path to run input directory (from Illumina machine)")

    args = parser.parse_args()

    run_pipeline(args.species, args.workdir, args.run)


if __name__ == "__main__":
    main()
