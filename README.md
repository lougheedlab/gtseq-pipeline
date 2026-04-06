# Lougheed Lab GTseq Pipeline

**WORK IN PROGRESS.**

GTseq pipeline derived from work done by Peiwen Li, [Kristen Hayward](https://github.com/kristenmhayward/GT-seq_2021), 
and others, with portions inspired by the [GTseq pipeline by Nate Campbell](https://github.com/GTseq/GTseq-Pipeline).


## System Requirements

This software must be run on a machine running Linux.


## Installation

1. Install/load [`bcl2fastq2`](https://support.illumina.com/downloads/bcl2fastq-conversion-software-v2-20.html) 
   if needed.
2. Install/load [`bcftools`](https://samtools.github.io/bcftools/bcftools.html) if needed.
3. Install the Lougheed Lab GTseq pipeline via `pip`:  `pip install lougheed_gtseq`
4. TODO


## Installation and Usage

### 1. Install dependencies

#### a. Install [`bcl2fastq2`](https://support.illumina.com/downloads/bcl2fastq-conversion-software-v2-20.html)

Follow the instructions on the linked page to install `bcl2fastq2`.

#### b. Obtain the GTSeq-Scripts pipeline (Nate Campbell)

Put this somewhere in a re-usable location (outside the current batch folder):

```bash
git clone https://github.com/GTseq/GTseq-Pipeline.git
```

### 2. Set up a virtual environment with `lougheed-gtseq` installed

```bash
python3 -m venv ./env
source env/bin/activate
pip install lougheed_gtseq
```

### 3. Prepare a sample sheet

It should have the following headers: `Sample_name`, `Plate_ID`, `i7_name`, `i5_name`.

There must be exactly one entry for a sample; additional replicates should have a unique suffix (e.g., `-1`, `-2`) added
to the end of the sample name.

### 4. Run the pipeline

TODO

#### If `bcl2fastq2` is needed (i.e., we are processing raw machine output):

```bash
lougheed-gtseq run --species polar --processes 10 --sex-calls APR2025.SexMarkers.genotypes_SNP.csv \
  APR2025 \
  250428_M04106_0147_000000000-M245M \
  APR2025_barcode.csv \
  APR2025.vcf
```

#### If we already have multiplexed R1/R2 files:

```bash
lougheed-gtseq run --species polar --processes 10 --sex-calls JUN2022.SexMarkers.genotypes_SNP.csv \
  --gtseq-scripts ~/bearwatch/GTseq-Pipeline \
  JUN2022 \
  JUN2022_L001_R1_001.fastq \
  --r2 JUN2022_L001_R2_001.fastq \
  JUN2022_barcode.csv \
  JUN2022.vcf
```


## Output

TODO


## Copyright Notice

Lougheed Lab GTseq pipeline. <br />
Copyright (C) 2024-2026  David Lougheed

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
