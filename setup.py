from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in gcash/__init__.py
from gcash import __version__ as version

setup(
	name="gcash",
	version=version,
	description="Gcash",
	author="jan",
	author_email="jan@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
