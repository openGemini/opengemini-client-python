from setuptools import setup, find_packages

setup(
    name="opengemini_client",
    version="0.0.1",
    author="shoothzj",
    author_email="shoothzj@gmail.com",
    description="A Python package for interacting with the opengemini",
    long_description_content_type="text/markdown",
    url="https://github.com/openGemini/opengemini-client-python.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
