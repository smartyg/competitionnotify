from setuptools import setup, find_packages

with open('README.md') as f:
	readme = f.read()

with open('LICENSE') as f:
	license = f.read()

setup(
	name='websocketframework',
	version='0.0.1',
	description='Framework to dynamically register modules (with commands) to listen on a websocket',
	long_description=readme,
	author='Martijn Goedhart',
	author_email='websocketframework@martijn-goedhart.nl',
	url='https://martijn-goedhart.nl/websocketframework',
	license=license,
	packages=find_packages(exclude=('tests', 'docs'))
)