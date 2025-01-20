from setuptools import setup, find_packages

setup(
    name="bifrost",
    version="0.0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "bifrost=bifrost_cli.bifrost:app",
        ],
    },
    install_requires=[
        "typer",
        "keyring",
        "pandas",
        "requests",
        "openpyxl",
        "xlsxwriter",
        "secretstorage",
    ],
)
