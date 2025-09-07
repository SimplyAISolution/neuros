from setuptools import setup, find_packages

# Read requirements from requirements.txt
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="neuros",
    version="0.1.0",
    author="NEUROS Team",
    author_email="support@neuros.ai",
    description="NEUROS: Neural Enhanced Universal Reasoning and Organizational System",
    long_description="NEUROS is a local-first AI memory and reasoning system that provides persistent memory and enhanced reasoning capabilities for personal AI interactions.",
    long_description_content_type="text/plain",
    url="https://github.com/SimplyAISolution/neuros",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "neuros=cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
