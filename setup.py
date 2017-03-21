from versionner import utils
utils.validate_python_version()

from codecs import open
from os import path
from setuptools import setup, find_packages


BASE_DIR = path.abspath(path.dirname(__file__))

with open(path.join(BASE_DIR, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='versionner',
    version='1.4.0',
    description='versionner helps manipulating version of the project.',
    long_description=long_description,
    url='http://msztolcman.github.io/versionner/',
    author='Marcin Sztolcman',
    author_email='marcin@urzenia.net',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
        'Topic :: Software Development',
        'Topic :: Software Development :: Documentation',
        'Topic :: Software Development :: Version Control',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['argparse', 'semver'],
    packages=find_packages(),
    package_data={'': ['LICENSE']},
    include_package_data=True,

    keywords='version management',

    entry_points={
        'console_scripts': [
            'ver=versionner.cli:main',
            'versionner=versionner.cli:main',
        ],
    },
)

