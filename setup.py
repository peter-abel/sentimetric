from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sentimetric",
    version="1.0.3",
    author="Abel Peter",
    author_email="peterabel791@gmail.com",
    description="A modern sentiment analysis library with optional LLM support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/peter-abel/sentimetric",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "openai": [
            "openai>=1.0.0",
        ],
        "google": [
            "google-generativeai>=0.3.0",
        ],
        "anthropic": [
            "anthropic>=0.25.0",
        ],
        "cohere": [
            "cohere>=5.0.0",
        ],
        "huggingface": [
            "huggingface-hub>=0.20.0",
        ],
        "all": [
            "openai>=1.0.0",
            "google-generativeai>=0.3.0",
            "anthropic>=0.25.0",
            "cohere>=5.0.0",
            "huggingface-hub>=0.20.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "sentimetric=sentimetric.sentiment:main",
        ],
    },
    keywords="sentiment analysis nlp machine-learning llm claude",
    project_urls={
        "Bug Reports": "https://github.com/peter-abel/sentimetric/issues",
        "Source": "https://github.com/peter-abel/sentimetric",
        "Documentation": "https://github.com/peter-abel/sentimetric#readme",

    },
)
