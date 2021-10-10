import copy
import gc
import io
import os
import unittest
import tempfile
from itertools import zip_longest

from pyhmmer import easel


EASEL_FOLDER = os.path.realpath(
    os.path.join(
        __file__,
        os.pardir,
        os.pardir,
        os.pardir,
        "vendor",
        "easel",
    )
)


class TestSequenceFile(unittest.TestCase):

    def test_init_error_unknownformat(self):
        with self.assertRaises(ValueError):
            _file = easel.SequenceFile("file.x", format="nonsense")

    def test_init_error_empty(self):
        with tempfile.NamedTemporaryFile() as empty:
            # without a format argument, we can't determine the file format
            self.assertRaises(ValueError, easel.SequenceFile, empty.name)
            # with a format argument, we don't expect the file to be empty
            self.assertRaises(EOFError, easel.SequenceFile, empty.name, "fasta")
        with io.BytesIO(b"") as buffer:
            # without a format argument, we can't determine the file format
            self.assertRaises(ValueError, easel.SequenceFile, buffer)
            # with a format argument, we don't expect the file to be empty
            self.assertRaises(EOFError, easel.SequenceFile, buffer, "fasta")

    def test_init_error_filenotfound(self):
        self.assertRaises(
            FileNotFoundError, easel.SequenceFile, "path/to/missing/file.fa"
        )

    def test_iter(self):
        fasta = os.path.join(EASEL_FOLDER, "formats", "fasta")

        with easel.SequenceFile(fasta) as f:
            seq1, seq2 = list(f)

        self.assertEqual(seq1.name, b"SNRPA_DROME")
        self.assertEqual(seq2.name, b"SNRPA_HUMAN")

    def test_parse(self):
        seq = easel.SequenceFile.parse(b"> EcoRI\nGAATTC\n", format="fasta")
        self.assertEqual(seq.name, b"EcoRI")

    def test_parse_error_unknownformat(self):
        with self.assertRaises(ValueError):
            _file = easel.SequenceFile.parse(b"> EcoRI\nGAATTC\n", format="nonsense")

    def test_read_skip_info(self):
        fasta = os.path.join(EASEL_FOLDER, "formats", "fasta")

        with easel.SequenceFile(fasta) as f:
            seq = f.read()
            self.assertEqual(seq.name, b"SNRPA_DROME")
            self.assertTrue(seq.sequence.startswith("MEMLPNQTIY"))

        with easel.SequenceFile(fasta) as f:
            seq = f.read(skip_info=True)
            self.assertEqual(seq.name, b"")
            self.assertTrue(seq.sequence.startswith("MEMLPNQTIY"))

    def test_read_skip_sequence(self):
        fasta = os.path.join(EASEL_FOLDER, "formats", "fasta")

        with easel.SequenceFile(fasta) as f:
            seq = f.read()
            self.assertEqual(seq.name, b"SNRPA_DROME")
            self.assertTrue(seq.sequence.startswith("MEMLPNQTIY"))

        with easel.SequenceFile(fasta) as f:
            seq = f.read(skip_sequence=True)
            self.assertEqual(seq.name, b"SNRPA_DROME")
            self.assertEqual(seq.sequence, "")

    def test_ignore_gaps(self):
        luxc = os.path.realpath(
            os.path.join(__file__, os.pardir, os.pardir, "data", "msa", "LuxC.faa")
        )
        # fails if not ignoring gaps (since if contains gaps)
        with easel.SequenceFile(luxc, "fasta") as seq_file:
            self.assertRaises(ValueError, seq_file.read)
        # succeeds if ignoring gaps
        with easel.SequenceFile(luxc, "fasta", ignore_gaps=True) as seq_file:
            sequences = list(seq_file)
            self.assertEqual(len(sequences), 13)


class _TestReadFilename(object):

    def test_read_filename_guess_format(self):
        # check reading a file without specifying the format works
        for filename, start in zip_longest(self.filenames, self.starts):
            path = os.path.join(self.folder, filename)
            with easel.SequenceFile(path) as f:
                seq = f.read()
                self.assertEqual(seq.sequence[:10], start)

    def test_read_filename_given_format(self):
        # check reading a file while specifying the format works
        for filename, start in zip_longest(self.filenames, self.starts):
            path = os.path.join(self.folder, filename)
            with easel.SequenceFile(path, self.format) as f:
                seq = f.read()
                self.assertEqual(seq.sequence[:10], start)

    def test_read_filename_count_sequences(self):
        # check reading a file while specifying the format works
        for filename, count in zip_longest(self.filenames, self.counts):
            path = os.path.join(self.folder, filename)
            with easel.SequenceFile(path, self.format) as f:
                sequences = list(f)
                self.assertEqual(len(sequences), count)

    def test_read_filename_guess_alphabet(self):
        for filename, alphabet in zip_longest(self.filenames, self.alphabet):
            path = os.path.join(self.folder, filename)
            with easel.SequenceFile(path, self.format) as f:
                if alphabet is not None:
                    self.assertEqual(f.guess_alphabet(), alphabet)
                else:
                    # FIXME: Until EddyRivasLab/easel#61 is merged, we cannot
                    #        test the case where `guess_alphabet` would throw
                    #        an error because of a bug in `sqascii_GuessAlphabet`
                    #        causing `eslEOD` to be returned when `eslNOALPHABET`
                    #        is expected.
                    pass


class _TestReadFileObject(object):

    def test_read_fileobject_given_format(self):
        # check reading a file while specifying the format works
        for filename, start in zip_longest(self.filenames, self.starts):
            path = os.path.join(self.folder, filename)
            with open(path, "rb") as f:
                buffer = io.BytesIO(f.read())
            with easel.SequenceFile(buffer, self.format) as f:
                seq = f.read()
                self.assertEqual(seq.sequence[:10], start)

    def test_read_fileobject_given_format(self):
        # check reading a file while specifying the format works
        for filename, start in zip_longest(self.filenames, self.starts):
            path = os.path.join(self.folder, filename)
            with open(path, "rb") as f:
                buffer = io.BytesIO(f.read())
            with easel.SequenceFile(buffer, self.format) as f:
                seq = f.read()
                self.assertEqual(seq.sequence[:10], start)

    def test_read_fileobject_count_sequences(self):
        # check reading a file while specifying the format works
        for filename, count in zip_longest(self.filenames, self.counts):
            path = os.path.join(self.folder, filename)
            with open(path, "rb") as f:
                buffer = io.BytesIO(f.read())
            with easel.SequenceFile(buffer, self.format) as f:
                sequences = list(f)
                self.assertEqual(len(sequences), count)

    def test_read_fileobject_guess_alphabet(self):
        for filename, alphabet in zip_longest(self.filenames, self.alphabet):
            path = os.path.join(self.folder, filename)
            with open(path, "rb") as f:
                buffer = io.BytesIO(f.read())
            with easel.SequenceFile(buffer, self.format) as f:
                if alphabet is not None:
                    self.assertEqual(f.guess_alphabet(), alphabet)
                else:
                    # FIXME: Until EddyRivasLab/easel#61 is merged, we cannot
                    #        test the case where `guess_alphabet` would throw
                    #        an error because of a bug in `sqascii_GuessAlphabet`
                    #        causing `eslEOD` to be returned when `eslNOALPHABET`
                    #        is expected.
                    pass


class TestEMBLFile(_TestReadFilename, _TestReadFileObject, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "formats")
    filenames = ["embl"]
    starts    = ["gaattcctga"]
    format    = "embl"
    counts    = [1]
    alphabet  = [easel.Alphabet.dna()]


class TestFastaFile(_TestReadFilename, _TestReadFileObject, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "formats")
    filenames = ["fasta", "fasta.2", "fasta.odd.1"]
    starts    = ["MEMLPNQTIY", "MEMLPNQTIY", ""]
    format    = "fasta"
    counts    = [2, 2, 2]
    alphabet  = [easel.Alphabet.amino(), easel.Alphabet.amino(), None]


class TestGenbankFile(_TestReadFilename, _TestReadFileObject, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "formats")
    filenames = ["genbank", "genbank.2"]
    starts    = ["atccacggcc", "atccacggcc"]
    format    = "genbank"
    counts    = [2, 2]
    alphabet  = [easel.Alphabet.dna(), easel.Alphabet.dna()]


class TestUniprotFile(_TestReadFilename, _TestReadFileObject, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "formats")
    filenames = ["uniprot"]
    starts    = ["MEMLPNQTIY"]
    format    = "uniprot"
    counts    = [1]
    alphabet  = [easel.Alphabet.amino()]


class TestA2MFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "a2m")
    filenames = ["a2m.good.1", "a2m.good.2"]
    starts    = ["VLSEGEWQLV", "UCCGAUAUAG"]
    format    = "a2m"
    counts    = [4, 5]
    alphabet  = [easel.Alphabet.amino(), easel.Alphabet.rna()]


class TestAlignedFastaFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "afa")
    filenames = ["afa.good.1", "afa.good.2", "afa.good.3"]
    starts    = ["VLSEGEWQLV", "UCCGAUAUAG", "mqifvktltg"]
    format    = "afa"
    counts    = [4, 5, 6]
    alphabet  = [easel.Alphabet.amino(), easel.Alphabet.rna(), easel.Alphabet.amino()]

    def test_read_filename_guess_format(self):
        unittest.skip("cannot guess format of aligned FASTA files")


class TestClustalFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "clustal")
    filenames = ["clustal.good.2"]
    starts    = ["UCCGAUAUAG"]
    format    = "clustal"
    counts    = [5]
    alphabet  = [easel.Alphabet.rna()]


class TestClustalLikeFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "clustal")
    filenames = ["clustal.good.1"]
    starts    = ["VLSEGEWQLV"]
    format    = "clustallike"
    counts    = [4]
    alphabet  = [easel.Alphabet.amino()]


class TestPhylipFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "phylip")
    filenames = ["phylip.good.1", "phylip.good.2", "phylip.good.3"]
    starts    = ["AAGCTNGGGC", "ATGGCGAAGG", "MKVILLFVLA"]
    format    = "phylip"
    counts    = [5, 7, 3]
    alphabet  = [easel.Alphabet.dna(), easel.Alphabet.dna(), easel.Alphabet.amino()]


class TestPhylipsFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "phylips")
    filenames = ["phylips.good.1", "phylips.good.2"]
    starts    = ["AAGCTNGGGC", "MKVILLFVLA"]
    format    = "phylips"
    counts    = [5, 3]
    alphabet  = [easel.Alphabet.dna(), easel.Alphabet.amino()]


class TestPsiblastFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "psiblast")
    filenames = ["psiblast.good.1", "psiblast.good.2"]
    starts    = ["VLSEGEWQLV", "UCCGAUAUAG"]
    format    = "psiblast"
    counts    = [4, 5]
    alphabet  = [easel.Alphabet.amino(), easel.Alphabet.rna()]


class TestSelexFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "selex")
    filenames = ["selex.good.1", "selex.good.2", "selex.good.3", "selex.good.4"]
    starts    = ["ACDEFGHIKL", "ACDEFGHIKL", "ACDEFGHIKL", "gGAGUAAGAU"]
    format    = "selex"
    counts    = [5, 5, 7, 11]
    alphabet  = [easel.Alphabet.amino(), easel.Alphabet.amino(), easel.Alphabet.amino(), easel.Alphabet.rna()]


class TestStockholmFile(_TestReadFilename, unittest.TestCase):
    folder    = os.path.join(EASEL_FOLDER, "esl_msa_testfiles", "stockholm")
    filenames = ["stockholm.good.1"]
    starts    = ["ACDEFGHKLM"]
    format    = "stockholm"
    counts    = [7]
    alphabet  = [easel.Alphabet.amino()]
