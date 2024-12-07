# Lougheed Lab GTseq Pipeline

GTseq pipeline derived from work done by Peiwen Li, Kristen Hayward, and others, with
portions inspired by the [GTseq pipeline by Nate Campbell](https://github.com/GTseq/GTseq-Pipeline).


## System Requirements

This software must be run on a machine running Linux.


## Installation

1. Install/load [`bcl2fastq2`](https://support.illumina.com/downloads/bcl2fastq-conversion-software-v2-20.html) 
   if needed.
2. Install/load [`bcftools`](https://samtools.github.io/bcftools/bcftools.html) if needed.
3. Install the Lougheed Lab GTseq pipeline via `pip`:  `pip install lougheed_gtseq`
4. TODO


## Usage

### 1. Prepare a sample sheet

It should have the following headers: `Sample_name`, `Plate_ID`, `i7_name`, `i5_name`.

There must be exactly one entry for a sample; additional replicates should have a unique suffix (e.g., `-1`, `-2`) added
to the end of the sample name.

### 2. TODO

TODO


## Copyright Notice

Lougheed Lab GTseq pipeline. <br />
Copyright (C) 2024  David Lougheed

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
