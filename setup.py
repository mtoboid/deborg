from setuptools import setup, find_packages

setup(
    name="deborg",
    version="0.0.1",
    description="Extract .deb packages from an emacs orgmode file.",
    author="Tobias Marczewski",
    extras_require=dict(tests=['pytest']),
    packages=find_packages(where='src'),
    package_dir={"": "src"}
)
