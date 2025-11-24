from setuptools import setup, find_packages

with open('README.md') as f:
	readme = f.read()

with open('LICENSE') as f:
	license = f.read()

setup(
	name='competitionnotify',
	version='0.0.1',
	description='Notify skaters of upcoming competitions on the KNSB (dutch) skating calendar',
	long_description=readme,
	author='Martijn Goedhart',
	author_email='competitionnotify@martijn-goedhart.nl',
	url='https://martijn-goedhart.nl/competitionnotify',
	license=license,
	#packages=["competitionnotify", "websocketframework", "taskmanager"],
	packages=find_packages(exclude=('tests', 'docs')),
	# package_dir={
	# 	"": ".",
	# 	"websocketframework": "websocketframework/websocketframework",
	# 	"taskmanager": "task-manager",
	# },
	# package_data={
	# 	"competitionnotify": ["py.typed"],
	# 	"websocketframework": ["py.typed"],
	# 	"taskmanager": ["py.typed"],
	# },
	python_requires=">=3.12, <4"
)