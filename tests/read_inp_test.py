import os
import unittest

from ccxinpreader import read_inp


class ReadImpTest(unittest.TestCase):

    def test_read_inp_with_simply_supported_2d_beam(self):
        """https://github.com/fandaL/beso/wiki/Example-1:-simply-supported-2D-beam"""
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '2d-beam.inp')

        result = read_inp(path)

        self.assertEqual(len(result['nodes'].keys()), 1159)
        self.assertEqual(len(result['elements'].keys()), 1080)

    def test_read_inp_with_multi_line_element_data(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'multi-line-element.inp')

        result = read_inp(path)

        self.assertEqual(len(result['nodes'].keys()), 20)
        self.assertListEqual(
            result['nodes'][1],
            [2.00000e+00, -7.45058e-09,  0.00000e+00])
        self.assertListEqual(
            result['nodes'][13],
            [2.50000e+00, -7.45058e-09,  0.00000e+00])

        self.assertEqual(len(result['elements'].keys()), 1)


if __name__ == '__main__':
    unittest.main()
