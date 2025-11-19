from setuptools import setup, find_packages

setup(
    name="python-function-generator",
    version="0.1.0",
    description="AI-powered Python function generator with documentation and tests",
    author="Karthi",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "litellm>=1.0.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "python-function-generator=function_generator.main:main",
        ],
    },
    python_requires=">=3.8",
)
