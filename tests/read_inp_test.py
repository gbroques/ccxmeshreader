import os
import unittest

from ccxinpreader import read_inp


class ImportImpTest(unittest.TestCase):

    def test_import_inp_with_simply_supported_2d_beam(self):
        """https://github.com/fandaL/beso/wiki/Example-1:-simply-supported-2D-beam"""
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '2DBeam.inp')

        result = read_inp(path)

        self.assertEqual(len(result['nodes'].keys()), 1159)
        self.assertEqual(len(result['elements'].keys()), 1080)


if __name__ == '__main__':
    unittest.main()
