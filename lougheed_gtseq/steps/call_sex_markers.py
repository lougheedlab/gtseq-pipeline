import os
import subprocess
from pathlib import Path

from ..models import SexCallingParams, Sample

__all__ = ["call_sex_markers"]


GENOTYPER = "GTseq_Genotyper_v3.pl"
GENO_COMPILE = "GTseq_GenoCompile_v3.pl"


def call_sex_markers(
    params: SexCallingParams, run_work_dir: Path, samples: list[Sample], sample_fastqs: dict[int, Path]
):
    # Ensure we have a sex-linked marker file, which should be in the Campbell format;
    # see https://github.com/GTseq/GTseq-Pipeline/blob/master/GTseq_Genotyper_v3.pl
    marker_file = Path(__file__).parent.parent / "alleles" / f"{params.species}.sl.csv"
    assert marker_file.exists()

    # Ensure we have a path to the Campbell et al. scripts:
    assert params.gtseq_scripts.is_dir()
    genotyper: Path = (params.gtseq_scripts / GENOTYPER).absolute()
    assert genotyper.is_file()
    geno_compile: Path = (params.gtseq_scripts / GENO_COMPILE).absolute()
    assert geno_compile.is_file()

    # Ensure we have an output path:
    output_path = params.sex_calls
    assert output_path is not None
    output_path = output_path.absolute()

    # Create output directory
    out_dir = run_work_dir / "sex_linked"
    genos_dir = out_dir / "genos"
    genos_dir.mkdir(parents=True, exist_ok=True)

    # For each sample, call sex-linked genotypes (Campbell et al. script)
    for si, fastq in sample_fastqs.items():
        sample = samples[si]
        print(f"Calling sex-linked markers for {sample.name} ({fastq=})")
        with open(genos_dir / f"{sample.plate}_{sample.name}.genos", "w") as fh:
            subprocess.check_call(("perl", str(genotyper), str(marker_file), str(fastq)), stdout=fh)
        print("    Done.")

    # Compile the genotypes into a single file (Campbell et al. script)
    cwd = os.getcwd()
    try:
        os.chdir(genos_dir)
        with open(output_path, "w") as fh:
            subprocess.check_call(("perl", str(geno_compile), "S", "0"), stdout=fh)
    finally:
        os.chdir(cwd)
