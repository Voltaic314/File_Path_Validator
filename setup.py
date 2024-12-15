from setuptools import setup, find_packages

setup(
    name='file-path-validator',
    version='2.3.4', 
    author='Logan',
    author_email='logan@stax.ai',
    description='A package for validating file paths across different operating systems and storage services.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Voltaic314/File_Path_Validator',
    packages=find_packages(),
    install_requires=open('FPV/requirements.txt', encoding='UTF-8').read().splitlines(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
