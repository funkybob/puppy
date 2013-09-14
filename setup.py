from setuptools import setup, find_packages

setup(
    name='django-puppy-cache',
    version='1.3.0',
    description='Django cache backend that helps prevent dog-piling.',
    author='Curtis Maloney',
    author_email='curtis@commoncode.com.au',
    url='http://github.com/funkybob/puppy',
    keywords=['django', 'redis', 'cache', 'memcached'],
    packages = find_packages(),
    zip_safe=False,
    requires = [
        'Django (>=1.5)',
    ],
    classifiers = [
        'Environment :: Web Environment',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)

