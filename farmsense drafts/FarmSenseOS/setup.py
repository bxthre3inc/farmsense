"""
FarmSense OS v1.0 - Installation Script

Ground-up deterministic farming operating system.
CLI-first, headless, Zo cloud-native.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="farmsense-os",
    version="1.0.0",
    author="Jeremy Beebe",
    author_email="getfarmsense@gmail.com",
    description="Deterministic Farming Operating System",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://farmsense.zo.computer",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Agriculture",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "farmsense=cli.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json"],
    },
)
