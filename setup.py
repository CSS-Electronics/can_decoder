import platform
import setuptools

from pathlib import Path


# Extract information from the README file and embed it in the package.
readme_path = Path(__file__).absolute().parent / "README.md"
with open(readme_path, "r") as fh:
    long_description = fh.read()

setuptools.setup(
    author="Magnus Aagaard Sørensen",
    author_email="mas@csselectronics.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 3 - Alpha",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    description="Utilities to decode CAN log files",
    install_requires=[
        "numpy",
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    name="can_decoder",
    packages=setuptools.find_packages(),
    python_requires='>=3.5',
    url="https://github.com/CSS-Electronics/can_decoder",
    version="0.0.3",
)
