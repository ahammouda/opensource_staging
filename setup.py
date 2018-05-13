import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-polls',
    version='0.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',
    description='Import data for Django models specified by arbitrarily complex dependency structures.',
    long_description=README,
    url='https://github.com/ahammouda/django_simple_imports',
    author='Adam Hammouda',
    author_email='adamhammouda3@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Development Status :: 3 - Alpha',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    # Taken from pip freeze
    install_requires=[
        'python-dateutil>=2.7.0',
        'flexible-dotdict>=0.2.1',
        'pytz>=2018.3',
        'six>=1.11.0'
    ],
    python_requires='>=3.6, <4',
)