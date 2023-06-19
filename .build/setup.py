from setuptools import setup, find_namespace_packages
from pathlib import Path

from rabbitmq_utils import __version__

# README FILE CONTENT
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# GETTING PACKAGES LIST
def get_packages_list():
    """Getting list of packages using requirements file."""
    requirements_file = this_directory / 'rabbitmq_utils' /  'requirements.txt'
    package_list = []
    for package in requirements_file.read_text().split('\n'):
        if package == '':
            continue
        package_list.append(package)
    return package_list

# def get_version():
#     """Getting version of the package."""
#     version_file = this_directory / 'rabbitmq_utils' / 'version.py'
#     with open(version_file, "rb") as source_file:
#         code = compile(source_file.read(), version_file, "exec")
#     exec(code)
#     return locals().get('__version__')

setup(
    name='rabbitmq-utils',
    version=__version__,
    description='Provide easy connection to rabbitmq server.',

    long_description=long_description,
    long_description_content_type='text/markdown',
    # url='https://hello.com',

    author='Tahir Rafique',
    author_email='tahirrafiqueasad@gmail.com',
    license='MIT',

    packages=find_namespace_packages(),
    package_data={
        "": ["*.txt"],
    },
    install_requires=get_packages_list(),

    keywords=["rabbitmq", "consumer", "producer", "publisher", 'subscriber'],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "Natural Language :: English",
    ]
)