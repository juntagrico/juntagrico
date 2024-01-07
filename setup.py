import os
from setuptools import find_packages, setup
import juntagrico

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)


def get_requirements(requirements_file):
    with open(requirements_file) as f:
        required = [line.split('#')[0] for line in f.read().splitlines()]
    return required


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    version=juntagrico.version,
    packages=find_packages(),
    include_package_data=True,
    install_requires=get_requirements(os.path.join(ROOT_DIR, 'requirements.txt')),
)
