import argparse
from pathlib import Path

from .models import Params
from .pipeline import run_pipeline
from .steps.run_qc import run_qc


def cmd_pipeline(args):
    params = Params(
        species=args.species,
        work_dir=args.work_dir,
        run=args.run,
        samples=args.samples,
        vcf=args.vcf,
        processes=args.processes,
    )

    run_pipeline(params)


def cmd_qc(args):
    run_qc(args.vcf_in, args.vcf_out)


def main():
    parser = argparse.ArgumentParser(prog="lougheed_gtseq")
    subparsers = parser.add_subparsers()

    # Run parser -------------------------------------------------------------------------------------------------------

    run_parser = subparsers.add_parser(
        "run", help="Run the complete GTseq genotyping pipeline."
    )
    run_parser.add_argument(
        "--species",
        type=str,
        help="Species/GTseq panel for the pipeline.",
        choices=("polar",),
    )
    run_parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path.cwd(),
        help="Working directory for reference genomes, alignments, etc.",
    )
    run_parser.add_argument(
        "--processes", "-p", type=int, help="Number of processes to use.", default=2
    )
    run_parser.add_argument(
        "run", type=Path, help="Path to run input directory (from Illumina machine)"
    )
    run_parser.add_argument("samples", type=Path, help="Path to sample sheet.")
    run_parser.add_argument("vcf", type=Path, help="VCF output file to generate.")

    run_parser.set_defaults(func=cmd_pipeline)

    # QC parser --------------------------------------------------------------------------------------------------------

    qc_parser = subparsers.add_parser("qc", help="Run the QC pipeline step on a VCF.")
    qc_parser.add_argument(
        "vcf_in",
        type=Path,
        help="The VCF input file to run the quality control step on.",
    )
    qc_parser.add_argument(
        "vcf_out",
        type=Path,
        help="The VCF output for the quality-controlled genotype data.",
    )
    qc_parser.set_defaults(func=cmd_qc)

    # ------------------------------------------------------------------------------------------------------------------

    args = parser.parse_args()

    if not getattr(args, "func", None):
        args = parser.parse_args(("--help",))

    args.func(args)


if __name__ == "__main__":
    main()
