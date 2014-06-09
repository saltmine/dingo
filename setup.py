from setuptools import setup, find_packages


setup(
  name='dingo',
  author='Steve Heinz',
  author_email='steve@keep.com',
  version='0.0.1',
  packages=find_packages(exclude=['tests*']),
  include_package_data=True,
  package_data={'dingo': ['dingo/etc/*']},
  url='http://keep.com',
  license='Private to keep.com',
  description='Fly-by-the-seat-of-your-pants resizing service',
  long_description=open('README').read(),
  zip_safe=False,
  install_requires=open('pip_requirements.txt').readlines(),
  dependency_links=open('dependency_links.txt').readlines(),
  entry_points={
    'console_scripts': [
      'dingo = dingo.commands:main',
      ]
    }
)
