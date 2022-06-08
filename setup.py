from setuptools import setup, find_packages

setup(
    name='commons',
    version='0.0.11',
    packages=find_packages(),
    install_requires=[
        'mss~=6.1.0',
        'multipledispatch~=0.6.0'
    ]
)
