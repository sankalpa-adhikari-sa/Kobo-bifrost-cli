from setuptools import setup, find_packages

setup(
    name="bifrost-cli",
    version="0.1",
    author="Sankalpa Adhikari",
    author_email="sankalpa.adhikari.sa@gmail.com",
    description="Commandline tool that helps you to create, update, deploy, redeploy, delete forms in Kobo-toolbox.",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'bifrost=bifrost_cli.bifrost:main',
        ],
    },
    install_requires=[
        "rich",
        "requests"
    ],
)