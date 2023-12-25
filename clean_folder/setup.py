from setuptools import setup, find_packages

setup(
    name='Clean folder',
    version='0.0.1',
    description='Sorts files by type and cleans empty folders',
    author='Pavlo Boichuk',
    author_email='pb@gmail.com',
    url='https://github.com/pavlo-boichuk/task_2',
    license='MIT',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['clean-folder=clean_folder.clean:main']
    }
)