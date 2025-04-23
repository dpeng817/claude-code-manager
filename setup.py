from setuptools import find_packages, setup

setup(
    name="claude-code-manager",
    version="0.1.0",
    description="A CLI tool for managing Claude Code temporary working environments",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/claude-code-manager",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "inquirer>=3.1.0",
        "rich>=13.0.0",
        "gitpython>=3.1.30",
        "pyyaml>=6.0",
        "click>=8.1.3",
    ],
    entry_points={
        "console_scripts": [
            "ccm=claude_code_manager.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    extras_require={
        "dev": [
            "ruff>=0.1.0",
            "uv>=0.24.0",
        ],
    },
)
