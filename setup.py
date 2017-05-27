from distutils.core import setup

setup(
    name='vitabs',
    version='0.1b',
    author='Pawel Stiasny',
    author_email='pawelstiasny@gmail.com',
    packages=['vitabs'],
    scripts=['bin/vitabs'],
    url='http://github.com/pstiasny/VITABS',
    license='GNU General Public License',
    description='Vi-inspired guitar tab editor',
    long_description=open('README').read(),
)
