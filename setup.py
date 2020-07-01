import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="iclppg", # Replace with your own username
    version="0.1",
    author="Ian Williams",
    author_email="",
    description="Raspberry pi - Max30101 ppg",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ilw/iclppg",
    packages=setuptools.find_packages(),
    package_data={
    'GUI': ['mainWindow.ui'],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT ",
        "Operating System :: Raspberry Pi Debian",
    ],
    python_requires='>=3.6',
)