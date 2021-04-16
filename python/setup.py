from setuptools import setup

setup(
    entry_points = {
        'console_scripts': [
            'democli=democli.cli:cli'
        ],
    }, install_requires=['requests', 'verboselogs', 'coloredlogs', 'dnspython', 'click']
)
