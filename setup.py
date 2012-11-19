from setuptools import setup, find_packages

VERSION = '1.0.0'

setup(
    name='puppy',
    version=VERSION,
    description='Django cache backend that helps prevent dog-piling.',
    author='Curtis Maloney',
    author_email='curtis@commoncode.com.au',
    url='http://github.com/commoncode/puppy',
    keywords=['django', 'redis', 'cache'],
    packages = find_packages(),
    zip_safe=False,
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

