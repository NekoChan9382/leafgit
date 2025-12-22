from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="leafgit",
    version="0.1.0",
    author="NekoChan9382",
    author_email="mushbeen25@gmail.com",
    description="Git/GitHub GUI client for beginners to learn Git operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NekoChan9382/leafgit",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.12",
    install_requires=[
        "PySide6>=6.6.0",
        "GitPython>=3.1.40",
        "PyGithub>=2.1.0",
        "cryptography>=41.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-qt>=4.2.0",
            "black>=23.0.0",
            "flake8>=6.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "leafgit=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["resources/*.json", "resources/icons/*", "resources/styles/*"],
    },
)
