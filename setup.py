from setuptools import setup, find_packages

with open("README.rst") as f:
    readme = f.read()

with open("LICENSE") as f:
    lic = f.read()

setup(
    name="Minimum Viable Block Chain",
    version="0.1.0",
    description="Simple implementation of a minimum viable blockchain",
    long_description=readme,
    author="Enrico Ringer",
    url="url",  # TODO
    license=lic,
    packages=find_packages(exclude='tests')
)
