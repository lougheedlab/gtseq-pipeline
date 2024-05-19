import re

__all__ = [
    "I7_BARCODES",
    "get_i7_barcode",
    "I5_BARCODES",
    "get_i5_barcode",
]

I7_BARCODES = {
    "001": "ATCACG",
    "002": "CGATGT",
    "003": "TTAGGC",
    "004": "TGACCA",
    "006": "GCCAAT",
    "012": "CTTGTA",
}


i7_barcode_numeral_pattern = re.compile(r"(0[0-1][1-6])")


def get_i7_barcode(val: str) -> str:
    m = i7_barcode_numeral_pattern.match(val)
    if not m:
        raise ValueError(f"Could not extract i7 barcode numeral from value: '{val}'")
    return m.group(1)


I5_BARCODES = {
    "A01": "AAACGG",
    "A02": "AACGTT",
    "A03": "AACTGA",
    "A04": "AAGACG",
    "A05": "AAGCTA",
    "A06": "AATATC",
    "A07": "AATGAG",
    "A08": "ACAAGA",
    "A09": "ACAGCG",
    "A10": "ACATAC",
    "A11": "ACCATG",
    "A12": "ACCCCC",
    "B01": "ACTCTT",
    "B02": "ACTGGC",
    "B03": "AGCCAT",
    "B04": "AGCGCA",
    "B05": "AGGGTC",
    "B06": "AGGTGT",
    "B07": "AGTAGG",
    "B08": "AGTTAA",
    "B09": "ATAGTA",
    "B10": "ATCAAA",
    "B11": "ATGCAC",
    "B12": "ATGTTG",
    "C01": "ATTCCG",
    "C02": "CAAAAA",
    "C03": "CAATCG",
    "C04": "CACCTC",
    "C05": "CAGGCA",
    "C06": "CATACT",
    "C07": "CCATTT",
    "C08": "CCCGGT",
    "C09": "CCCTAA",
    "C10": "CCGAGG",
    "C11": "CCGCAT",
    "C12": "CCTAAC",
    "D01": "CGAGGC",
    "D02": "CGCAGA",
    "D03": "CGCGTG",
    "D04": "CGGTCC",
    "D05": "CGTCTA",
    "D06": "CGTGAT",
    "D07": "CTACAG",
    "D08": "CTCGCC",
    "D09": "CTGCGA",
    "D10": "CTGGTT",
    "D11": "CTTATG",
    "D12": "CTTTGC",
    "E01": "GAAATG",
    "E02": "GAACCA",
    "E03": "GACGAC",
    "E04": "GACTCT",
    "E05": "GAGAGA",
    "E06": "AATCGT",
    "E07": "GCAGAT",
    "E08": "GCATGG",
    "E09": "GCCGTA",
    "E10": "GCGACC",
    "E11": "GCGCTG",
    "E12": "GCTCAA",
    "F01": "GGACTT",
    "F02": "GGCAAG",
    "F03": "GGGCGC",
    "F04": "GGGGCG",
    "F05": "GGTACA",
    "F06": "GGTTTG",
    "F07": "GTAAGT",
    "F08": "GTATCC",
    "F09": "GTCATC",
    "F10": "GTGCCT",
    "F11": "GTGTAA",
    "F12": "GTTGGA",
    "G01": "TAAGCT",
    "G02": "TAATTC",
    "G03": "TACACA",
    "G04": "TACGGG",
    "G05": "TAGTAT",
    "G06": "TATCAC",
    "G07": "TCAAAG",
    "G08": "TCCTGC",
    "G09": "TCGATT",
    "G10": "TCGCCA",
    "G11": "TCGGAC",
    "G12": "TCTCGG",
    "H01": "TCTTCT",
    "H02": "TGAACC",
    "H03": "TGACAA",
    "H04": "TGCCCG",
    "H05": "TGCTTA",
    "H06": "TGGGGA",
    "H07": "TTATGA",
    "H08": "TTCCGT",
    "H09": "TTCTAG",
    "H10": "TTGAGC",
    "H11": "TTTAAT",
    "H12": "TTTGTC",
}


r_i5_canonical = re.compile(r"^([A-H])([01]\d)$")  # first form: A01, A02, ...
r_i5_alternate = re.compile(r"^(\d|1[0-2])([A-H])$")  # second form: 1A, 2A, ...


def get_i5_barcode(coordinate: str):
    if r_i5_canonical.match(coordinate):  # canonical form
        return I5_BARCODES[coordinate]
    elif m := r_i5_alternate.match(coordinate):  # alternate form; need to transform
        return I5_BARCODES[f"{m.group(2)}{m.group(1).zfill(2)}"]
    else:
        raise ValueError("Invalid coordinate for Lougheed GTseq panel")
