import pytest

from lougheed_gtseq.barcodes import I7_BARCODES, get_i7_barcode, I5_BARCODES, get_i5_barcode


def test_extract_i7():
    assert get_i7_barcode("GTseq i7 003 10uM") == I7_BARCODES["003"]


def test_extract_i7_errs():
    with pytest.raises(ValueError):
        get_i7_barcode("GTseq i7 10uM")  # no numeral

    with pytest.raises(ValueError):
        get_i7_barcode("GTseq i7 005 10uM")  # numeral doesn't have an associated barcode


def test_extract_i5():
    assert get_i5_barcode("A01") == I5_BARCODES["A01"]
    assert get_i5_barcode("A1") == I5_BARCODES["A01"]
    assert get_i5_barcode("1A") == I5_BARCODES["A01"]
