import os
import unittest

from ccxmeshreader import ParserError, read_mesh


class ReadMeshTest(unittest.TestCase):

    def test_read_mesh_with_simply_supported_2d_beam(self):
        """https://github.com/fandaL/beso/wiki/Example-1:-simply-supported-2D-beam"""
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), '2d-beam.inp')

        mesh = read_mesh(path)

        self.assertEqual(len(mesh['node_coordinates_by_number'].keys()), 1159)
        self.assertTupleEqual(mesh['node_coordinates_by_number'][1], (0, 0, 0))
        self.assertTupleEqual(
            mesh['node_coordinates_by_number'][2], (0, 18, 0))
        self.assertTupleEqual(
            mesh['node_coordinates_by_number'][530], (1.991512192678, 2.992319281912, 0))
        self.assertTupleEqual(
            mesh['node_coordinates_by_number'][1158], (22, 9, 0))
        self.assertTupleEqual(
            mesh['node_coordinates_by_number'][1159], (19, 9, 0))

        self.assertEqual(len(mesh['element_dict_by_type'].keys()), 1)
        self.assertEqual(len(mesh['element_dict_by_type']['S4'].keys()), 1080)
        self.assertListEqual(mesh['element_dict_by_type']['S4'][157],
                             [193, 283, 392, 282])
        self.assertListEqual(mesh['element_dict_by_type']['S4'][179],
                             [852, 987, 1009, 943])
        self.assertListEqual(mesh['element_dict_by_type']['S4'][1132],
                             [934, 1053, 1128, 1020])
        self.assertListEqual(mesh['element_dict_by_type']['S4'][1236],
                             [6, 5, 193, 282])

        self.assertTrue('EFACES' in mesh['element_set_by_name'])
        self.assertTrue(157 in mesh['element_set_by_name']['EFACES'])
        self.assertTrue(179 in mesh['element_set_by_name']['EFACES'])
        self.assertTrue(1132 in mesh['element_set_by_name']['EFACES'])
        self.assertTrue(1236 in mesh['element_set_by_name']['EFACES'])

        self.assertTrue(mesh['element_set_by_name']['EALL'] ==
                        mesh['element_set_by_name']['EFACES'])
        self.assertTrue(mesh['element_set_by_name']['SOLIDMATERIALELEMENTGEOMETRY2D']
                        == mesh['element_set_by_name']['EFACES'])

    def test_read_mesh_with_continuation_line_element_data(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'continuation-line-element.inp')

        mesh = read_mesh(path)

        self.assertEqual(len(mesh['node_coordinates_by_number'].keys()), 20)
        self.assertTupleEqual(
            mesh['node_coordinates_by_number'][1],
            (2.00000e+00, -7.45058e-09,  0.00000e+00))
        self.assertTupleEqual(
            mesh['node_coordinates_by_number'][13],
            (2.50000e+00, -7.45058e-09,  0.00000e+00))

        self.assertEqual(len(mesh['element_dict_by_type'].keys()), 1)
        self.assertEqual(len(mesh['element_dict_by_type']['C3D20R'].keys()), 1)
        self.assertListEqual(
            mesh['element_dict_by_type']['C3D20R'][1],
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])

        self.assertEqual(mesh['element_set_by_name']['EALL'], {1})
        self.assertEqual(mesh['element_set_by_name']['E1'], {1, 2, 3, 4, 5})
        self.assertEqual(mesh['element_set_by_name']['E2'], {1, 2, 3, 4, 5, 6, 7})
        self.assertEqual(mesh['element_set_by_name']['E3'], {1, 3, 5, 7})
        self.assertEqual(mesh['element_set_by_name']['E4'], {20})

    def test_read_mesh_with_continuation_keyword_line_raises_parser_error(self):
        path = os.path.join(os.path.abspath(
            os.path.dirname(__file__)), 'continuation-keyword-line.inp')

        with self.assertRaises(ParserError) as context:
            read_mesh(path)
            self.assertEqual(
                'Continuation of keyword lines not supported.', context.exception)


if __name__ == '__main__':
    unittest.main()
