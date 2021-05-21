from setuptools import find_packages, setup

setup(
    name='beeminder_stopwatch',
    version='0.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'PySimpleGUI',
        'requests'
    ],
)
