from setuptools import setup, find_packages

setup(
    name="bifrost-cli",
    version="0.1",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bifrost=bifrost_cli.bifrost:main',
        ],
    },
    install_requires=[
        "click",
        "rich",
        "requests"
    ],
)