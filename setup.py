from setuptools import setup, find_packages

setup(
    name='path_validator',  # Replace with your package name
    version='0.1.0',  # Version of your package
    author='Logan',  # Your name or your organization
    author_email='your.email@example.com',  # Your email address
    description='A package for validating file paths across different operating systems',  # A short description of your package
    long_description=open('README.md').read(),  # Optional: a longer description, e.g., from a README file
    long_description_content_type='text/markdown',  # Format of the long description
    url='https://github.com/yourusername/path_validator',  # URL to your package repository
    packages=find_packages(where='src'),  # Automatically find packages in the src directory
    package_dir={'': 'src'},  # Tell distutils packages are under src
    install_requires=open('src/requirements.txt').read().splitlines(),  # Requirements from the requirements.txt
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',  # Specify your license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',  # Minimum Python version requirement
)
