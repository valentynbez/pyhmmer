import io
import itertools
import os
import shutil
import unittest
import tempfile
import pkg_resources

import pyhmmer
from pyhmmer.errors import EaselError
from pyhmmer.easel import SequenceFile
from pyhmmer.plan7 import HMMFile, Pipeline


# --- Mixins -------------------------------------------------------------------

class _TestHMMFile:

    ID = NotImplemented
    NAMES = NotImplemented

    @classmethod
    def setUpClass(cls):
        cls.hmms_folder = pkg_resources.resource_filename("tests", "data/hmms")

    def open_hmm(self, path):
        raise NotImplementedError()

    def check_hmmfile(self, hmmfile):
        for hmm, expected in itertools.zip_longest(hmmfile, self.NAMES):
            self.assertIsNot(hmm, None, "missing HMM: {}".format(expected))
            self.assertIsNot(expected, None, "unexpected extra HMM: {}".format(hmm))
            self.assertEqual(hmm.name, expected)
            self.assertIsNot(hmm.cutoffs, None)
            self.assertIsNot(hmm.evalue_parameters, None)

    def test_empty(self):
        with tempfile.NamedTemporaryFile() as empty:
            self.assertRaises(EOFError, self.open_hmm, empty.name)

    def test_read_hmmpressed(self):
        path = os.path.join(self.hmms_folder, "db", "{}.hmm.h3m".format(self.ID))
        with self.open_hmm(path) as f:
            self.check_hmmfile(f)

    def test_read_h3m(self):
        path = os.path.join(self.hmms_folder, "bin", "{}.h3m".format(self.ID))
        with self.open_hmm(path) as f:
            self.check_hmmfile(f)

    def test_read_hmm3(self):
        path = os.path.join(self.hmms_folder, "txt", "{}.hmm".format(self.ID))
        with self.open_hmm(path) as f:
            self.check_hmmfile(f)

    def test_read_hmm2(self):
        path = os.path.join(self.hmms_folder, "txt2", "{}.hmm2".format(self.ID))
        with self.open_hmm(path) as f:
            self.check_hmmfile(f)


class _TestHMMFileobj:

    def open_hmm(self, path):
        with open(path, "rb") as f:
            buffer = io.BytesIO(f.read())
        return HMMFile(buffer)


class _TestHMMPath:

    def open_hmm(self, path):
        return HMMFile(path)

    def test_filenotfound(self):
        self.assertRaises(FileNotFoundError, HMMFile, "path/to/missing/file")


class _TestThioesterase(_TestHMMFile):
    ID = "Thioesterase"
    NAMES = [b"Thioesterase"]


class _TestT2PKS(_TestHMMFile):
    ID = "t2pks"
    NAMES = [
        b"CLF", b"CLF_7", b"CLF_8|9", b"CLF_11|12", b"AT", b"CYC", b"CYC_C7-C12",
        b"CYC_C5-C14", b"CYC_C5-C14/C3-C16", b"CYC_C1-C18|C2-C19", b"CYC_C2-C19",
        b"CYC_C5-C18", b"CYC_C4-C17/C2-C19", b"CYC_C4-C21/C2-C23|C2-C19",
        b"CYC_C9-C14", b"KSIII", b"ACP", b"KR", b"KR_C9", b"KR_C11", b"KR_C15",
        b"KR_C17", b"KR_C19", b"KS", b"OXY", b"GT", b"MET", b"MET_carboxy_O",
        b"MET_C2O|C2N", b"MET_C6|C8", b"MET_C9O", b"MET_C10", b"MET_C11O",
        b"MET_C13O|C17O", b"MET_C18O", b"DIMER", b"LIG", b"HAL", b"AMIN",
        b"AMID"
    ]


# --- Test cases ---------------------------------------------------------------


class TestFileobjSingle(_TestHMMFileobj, _TestThioesterase, unittest.TestCase):
    pass

class TestFileObjMultiple(_TestHMMFileobj, _TestT2PKS, unittest.TestCase):
    pass

class TestPathSingle(_TestHMMPath, _TestThioesterase, unittest.TestCase):
    pass

class TestPathMultiple(_TestHMMPath, _TestT2PKS, unittest.TestCase):
    pass
