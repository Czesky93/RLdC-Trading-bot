from setuptools import setup, find_packages

setup(
    name='trading_module',
    version='1.0.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'trading=trading.trading:trading_function'
        ]
    }
)
