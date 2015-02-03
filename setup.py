from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    readme = f.read()


setup(
    name='nyaalib',
    version='0.0.1',
    description='Python library for Nyaa',
    long_description=readme,
    url='https://github.com/kennydo/nyaalib',
    author='Kenny Do',
    author_email='kedo@ocf.berkeley.edu',
    license='MIT',
    classifiers=[

    ],
    packages=find_packages(),
    install_requires=[
        'html5lib',
        'requests',
    ],
)
