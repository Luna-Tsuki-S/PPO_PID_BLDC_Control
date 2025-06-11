from setuptools import setup, find_packages

setup(
    name="opcua_client_pkg",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "opcua",
    ],
    author="你的名字",
    description="OPC UA Client 封裝模組",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
