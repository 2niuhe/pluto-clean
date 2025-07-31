from setuptools import setup, find_packages

setup(
    name="pluto-clean",
    version="0.1.0",
    description="Generate synthetic data for LLM fine-tuning with multi-provider support",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["litellm>=1.74.0"],
    python_requires=">=3.7",
    author="Carlton",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
