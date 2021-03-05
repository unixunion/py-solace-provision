import os
from setuptools import setup
from os import path
from setuptools.command.install import install

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

# Fetch version from git tags, and write to version.py.
# Also, when git is not available (PyPi package), use stored version.py.
version_py = os.path.join(os.path.dirname(__file__), 'version.py')

with open(version_py, 'rt') as fh:
    version = "%s" % fh.read().strip().split('=')[-1].replace('"', '').strip()
    print("setting version from file: %s" % version)

print("version: %s" % version)

# sempver = None

# class InstallCommand(install):
#     user_options = install.user_options + [
#         # ('someopt', None, None), # a 'flag' option
#         ('sempver=', None, None)  # an option that takes a value
#     ]
#
#     def initialize_options(self):
#         install.initialize_options(self)
#         self.sempver = None
#         # self.someval = None
#
#     def finalize_options(self):
#         print("value of someopt is", self.sempver)
#         install.finalize_options(self)
#
#     def run(self):
#         global sempver
#         sempver = self.sempver  # will be 1 or None
#         install.run(self)
#

setup(
    # cmd={
    #     'install': InstallCommand
    # },
    name="py-solace-provision",
    version=version,
    author="Kegan Holtzhausen",
    author_email="marzubus@gmail.com",
    description="A solace provisioning toolkit",
    license="BSD",
    keywords="solace messaging provioning",
    url="https://github.com/unixunion/py-solace-provision",
    packages=['sp'],
    scripts=["pysolpro.py"],
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'libkplug',
        'six',
        'pyyaml'
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ]
)

print("test")
