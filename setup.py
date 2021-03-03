import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="py-solace-provision",
    version="0.5.0",
    author="Kegan Holtzhausen",
    author_email="marzubus@gmail.com",
    description="A solace provisioning toolkit",
    license="BSD",
    keywords="solace messaging provioning",
    url="https://github.com/unixunion/py-solace-provision",
    packages=['sp', 'sp.legacy'],
    scripts=["pysolpro.py"],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
