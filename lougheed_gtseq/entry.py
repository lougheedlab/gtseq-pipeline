import argparse
import sys

from pathlib import Path


def cmd_pipeline(args):
    from .models import Params
    from .pipeline import run_pipeline

    call_sex = not args.no_sex_calls
    gtseq_scripts_path: Path = args.gtseq_scripts
    sex_calls: Path | None = args.sex_calls
    r2: Path | None = args.r2

    if call_sex:
        if sex_calls is None:
            print(
                "--sex-calls output CSV file for sex marker genotype output must be specified with --no-sex-calls is "
                "not set.",
                file=sys.stderr,
            )
            exit(1)

        if not gtseq_scripts_path.exists():
            print(
                "--gtseq-scripts must point to a directory containing the contents of the "
                "https://github.com/GTseq/GTseq-Pipeline/ repository.",
                file=sys.stderr,
            )
            exit(1)

    params = Params(
        species=args.species,
        work_dir=args.work_dir,
        run=args.run if r2 is None else (args.run, args.r2),
        samples=args.samples,
        call_sex=call_sex,
        gtseq_scripts=args.gtseq_scripts,
        min_dp=args.min_dp,
        min_gq=args.min_gq,
        min_called_prop=args.min_called_prop,
        het_sigma=args.het_sigma,
        drop_failed_samples=args.drop_failed,
        vcf=args.vcf,
        sex_calls=args.sex_calls,
        continue_run=args.continue_run,
        genomes=args.genomes,
        processes=args.processes,
    )

    run_pipeline(params)


def cmd_qc(args):
    from .steps.run_qc import run_qc

    run_qc(
        Path.cwd(),
        args.vcf_in,
        args.vcf_out,
        args.min_dp,
        args.min_gq,
        args.min_called_prop,
        args.het_sigma,
        args.drop_failed,
    )


def cmd_snp_success(args):
    from .snp_success import run_snp_success

    run_snp_success(args.vcf)


def cmd_reheader(args):
    from .logger import logger
    from .steps.reheader import run_reheader

    run_reheader(args, logger)


QC_DEFAULT_MIN_DP: int = 6
QC_DEFAULT_MIN_GQ: int = 18
QC_DEFAULT_MIN_CALLED_PROP: float = 0.75
QC_DEFAULT_HET_SIGMA: int = 2


def _add_qc_args(subparser):
    subparser.add_argument(
        "--min-dp",
        type=int,
        default=QC_DEFAULT_MIN_DP,
        help="Required minimum read depth for a sample call to pass QC.",
    )
    subparser.add_argument(
        "--min-gq",
        type=int,
        default=QC_DEFAULT_MIN_GQ,
        help="Required minimum PHRED genotype quality for a sample call to pass QC.",
    )
    subparser.add_argument(
        "--min-called-prop",
        type=float,
        default=QC_DEFAULT_MIN_CALLED_PROP,
        help="Required minimum proportion of successfully-called loci to include a sample.",
    )
    subparser.add_argument(
        "--het-sigma",
        type=int,
        default=QC_DEFAULT_HET_SIGMA,
        help="Number of standard deviations from the mean heterozygosity allowable before a sample fails QC.",
    )
    subparser.add_argument(
        "--drop-failed",
        action="store_true",
        help="Whether to exclude samples which fail the QC threshold for loci called.",
    )


def main():
    parser = argparse.ArgumentParser(prog="lougheed_gtseq")
    subparsers = parser.add_subparsers()

    # Run parser -------------------------------------------------------------------------------------------------------

    run_parser = subparsers.add_parser("run", help="Run the complete GTseq genotyping pipeline.")
    run_parser.add_argument(
        "--species",
        type=str,
        help="Species/GTseq panel for the pipeline.",
        choices=("polar",),
        required=True,
    )
    _add_qc_args(run_parser)
    run_parser.add_argument(
        "--work-dir",
        type=Path,
        default=Path.cwd(),
        help="Working directory for reference genomes, alignments, etc.",
    )
    run_parser.add_argument(
        "--gtseq-scripts",
        type=Path,
        default=Path.cwd() / "GTseq-Pipeline",
        help="Directory holding GTseq pipeline scripts from Campbell et al.",
    )
    run_parser.add_argument(
        "--no-sex-calls",
        action="store_true",
        help="Turns off the sex marker calling part of the pipeline.",
    )
    run_parser.add_argument(
        "--genomes",
        type=Path,
        help="Location for shared reference genome resources. Downloaded genomes will be put here.",
    )
    run_parser.add_argument("--processes", "-p", type=int, help="Number of processes to use.", default=4)
    run_parser.add_argument("--continue-run", type=Path, help="Continue/restart an existing run.")
    run_parser.add_argument(
        "run",
        type=Path,
        help="Path to run input directory (from Illumina machine) or R1 FASTQ file (if --r2 is passed as well.)",
    )
    run_parser.add_argument("batch", type=str, help="Batch ID (e.g., APR2025).")
    run_parser.add_argument("samples", type=Path, help="Path to sample sheet.")
    run_parser.add_argument("vcf", type=Path, help="VCF output file to generate.")
    run_parser.add_argument("--sex-calls", type=Path, help="Output file for sex calls CSV.")
    run_parser.add_argument("--r2", type=Path, help="Path to R2 FASTQ file (if skipping bcl2fastq2 step.")

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
    _add_qc_args(qc_parser)
    qc_parser.set_defaults(func=cmd_qc)

    # ------------------------------------------------------------------------------------------------------------------

    reheader_parser = subparsers.add_parser("reheader", help="Reheader VCF with normalized sample names.")
    reheader_parser.add_argument("batch", type=str, help="Batch ID (e.g., APR2025).")
    reheader_parser.add_argument("samples", type=Path, help="Path to sample sheet.")
    reheader_parser.add_argument("vcf", type=Path, help="The VCF to reheader.")
    reheader_parser.set_defaults(func=cmd_reheader)

    # ------------------------------------------------------------------------------------------------------------------

    success_parser = subparsers.add_parser("snp-success", help="Calculate call success rates of SNPs in a VCF.")
    success_parser.add_argument("vcf", type=Path, help="The VCF to calculate SNP success rates for.")
    success_parser.set_defaults(func=cmd_snp_success)

    # ------------------------------------------------------------------------------------------------------------------

    het_parser = subparsers.add_parser("het", help="Calculate heterozygosity of a sample in a VCF.")
    het_parser.add_argument("vcf", type=Path, help="The")

    # ------------------------------------------------------------------------------------------------------------------

    args = parser.parse_args()

    if not getattr(args, "func", None):
        args = parser.parse_args(("--help",))

    args.func(args)


if __name__ == "__main__":
    main()
