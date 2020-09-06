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
        self.assertListEqual(result['nodes'][1], [0, 0, 0])
        self.assertListEqual(result['nodes'][2], [0, 18, 0])
        self.assertListEqual(
            result['nodes'][530], [1.991512192678, 2.992319281912, 0])
        self.assertListEqual(result['nodes'][1158], [22, 9, 0])
        self.assertListEqual(result['nodes'][1159], [19, 9, 0])

        self.assertEqual(len(result['elements'].keys()), 1)
        self.assertEqual(len(result['elements']['S4'].keys()), 1080)
        self.assertListEqual(result['elements']['S4'][157],
                             [193, 283, 392, 282])
        self.assertListEqual(result['elements']['S4'][179],
                             [852, 987, 1009, 943])
        self.assertListEqual(result['elements']['S4'][1132],
                             [934, 1053, 1128, 1020])
        self.assertListEqual(result['elements']['S4'][1236],
                             [6, 5, 193, 282])

        self.assertTrue('EFACES' in result['element_sets'])
        self.assertTrue(157 in result['element_sets']['EFACES'])
        self.assertTrue(179 in result['element_sets']['EFACES'])
        self.assertTrue(1132 in result['element_sets']['EFACES'])
        self.assertTrue(1236 in result['element_sets']['EFACES'])

        self.assertTrue(result['element_sets']['EALL'] == result['element_sets']['EFACES'])
        self.assertTrue(result['element_sets']['SOLIDMATERIALELEMENTGEOMETRY2D'] == result['element_sets']['EFACES'])

    def test_read_inp_with_continuation_line_element_data(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'continuation-line-element.inp')

        result = read_inp(path)

        self.assertEqual(len(result['nodes'].keys()), 20)
        self.assertListEqual(
            result['nodes'][1],
            [2.00000e+00, -7.45058e-09,  0.00000e+00])
        self.assertListEqual(
            result['nodes'][13],
            [2.50000e+00, -7.45058e-09,  0.00000e+00])

        self.assertEqual(len(result['elements'].keys()), 1)
        self.assertEqual(len(result['elements']['C3D20R'].keys()), 1)
        self.assertListEqual(
            result['elements']['C3D20R'][1],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

        self.assertEqual(result['element_sets']['EALL'], {1})
        self.assertEqual(result['element_sets']['E1'], {1, 2, 3, 4, 5})
        self.assertEqual(result['element_sets']['E2'], {1, 2, 3, 4, 5, 6, 7})
        self.assertEqual(result['element_sets']['E3'], {1, 3, 5, 7})
        self.assertEqual(result['element_sets']['E4'], {20})

if __name__ == '__main__':
    unittest.main()
