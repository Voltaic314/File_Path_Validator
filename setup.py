from setuptools import setup, find_packages

setup(
    name='file-path-validator',
    version='1.5', 
    author='Logan',
    author_email='logan@stax.ai',
    description='A package for validating file paths across different operating systems',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Voltaic314/File_Path_Validator',
    packages=find_packages(),
    install_requires=open('FPV/requirements.txt').read().splitlines(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
