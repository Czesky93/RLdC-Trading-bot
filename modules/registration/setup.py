from setuptools import setup, find_packages

setup(
    name='registration_module',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'registration=registration.registration:registration_function'
        ]
    }
)
