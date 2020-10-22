import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="isf-converter-py",
    version="1.0",
    author="Konstantin Shpakov",
    author_email="konstantine.shpakov@gmail.com",
    description="ISF binary file reader module and ISF-CSV batch file conversion tool with CLI.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shpakovkv/isf-converter-py",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
