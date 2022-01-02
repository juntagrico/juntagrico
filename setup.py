import os
from setuptools import find_packages, setup
import juntagrico

ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


def get_requirements(requirements_file):
    with open(requirements_file) as f:
        required = [line.split('#')[0] for line in f.read().splitlines()]
    return required


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='juntagrico',
    version=juntagrico.version,
    packages=find_packages(),
    include_package_data=True,
    license='GNU Lesser General Public License v3 (LGPLv3)',
    description='juntagrico',
    long_description=README,
    url='https://www.juntagrico.org',
    author='juntagrico',
    author_email='python@juntagrico.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8 ',
        'Programming Language :: Python :: 3.9 ',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=get_requirements(os.path.join(ROOT_DIR, 'requirements.txt')),
)
