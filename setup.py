import io
from os import path

from setuptools import setup

current_dir = path.abspath(path.dirname(__file__))
with io.open(path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ccxmeshreader',
    description='Reads a mesh from CalcluliX input (.inp) files.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/gbroques/ccxmeshreader',
    author='G Roques',
    version='0.1.0',
    packages=['ccxmeshreader'],
    install_requires=[],
    classifiers=[
        # Full List: https://pypi.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Programming Language :: Python :: 3 :: Only'
    ]
)
