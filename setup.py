from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="azcam-vatt",
    version="20.3",
    description="azcam environment for VATT",
    long_description=long_description,
    author="Michael Lesser",
    author_email="mlesser@arizona.edu",
    keywords="python parameters",
    packages=find_packages(),
    zip_safe=False,
    install_requires=[],
)
