from distutils.core import setup

setup(
	name='VITABS',
	version='0.1dev',
	author='Pawel Stiasny',
	packages=['vitabs'],
	scripts=['bin/vitabs', 'bin/vitabs-song'],
	url='http://github.com/PawelStiasny/VITABS',
	license='COPYING',
	description='Vi-inspired guitar tab editor',
	long_description=open('README').read(),
)
