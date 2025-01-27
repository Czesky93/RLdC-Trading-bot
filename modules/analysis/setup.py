from setuptools import setup, find_packages

setup(
    name='analysis_module',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'analysis=analysis.analysis:analysis_function'
        ]
    }
)
