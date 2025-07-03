from setuptools import setup, find_packages

setup(
    name='file-path-validator',
    version='3.1.0', 
    author='Logan',
    author_email='lmaupin754@gmail.com',
    description='A package for validating file paths across different operating systems and storage services.',
    long_description=open('README.md', encoding='UTF-8').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Voltaic314/File_Path_Validator',
    packages=find_packages(),
    install_requires=open(r'C:\Users\golde\OneDrive\Documents\GitHub\File_Path_Validator\FPV\requirements.txt', encoding='UTF-8').read().splitlines(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    license='MIT',
)
