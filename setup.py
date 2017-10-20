"""package setup"""

import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


__version__ = '0.0.2'


class PyTest(TestCommand):
    """Our test runner."""

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ["src"]

    def finalize_options(self):
        # pylint: disable=W0201
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name="pyramid_objective",
    author="Oliver Berger",
    author_email="diefans@gmail.com",
    url="https://github.com/diefans/pyramid_objective",
    description="declaraive de/serialization of python structures for pyramid",
    version=__version__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
    ],

    keywords="objective pyramid deserialization serialization",

    package_dir={'': 'src'},
    namespace_packages=[],
    packages=find_packages(
        'src',
        exclude=[]
    ),
    entry_points="",

    install_requires=[
        # pyramid
        "pyramid",

        # zope
        'zope.component',

        # data
        'objective',
    ],

    cmdclass={'test': PyTest},
    tests_require=[
        # tests
        'pytest',
        'pytest-pep8',
        'pytest-random',
        'mock',
    ]
)
