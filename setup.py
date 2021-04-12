from setuptools import find_packages, setup
import version

with open("README.md", "r") as fh:
    LONG_DESCRIPTION = fh.read()
    print(LONG_DESCRIPTION)

with open('requirements.txt') as f:
    REQUIREMENTS = f.read().splitlines()

setup(
    name='robotframework-historic-parser',
    version=version.VERSION,
    description='Parser to push robotframework execution results to MySQL',
    classifiers=[
          'Framework :: Robot Framework',
          'Programming Language :: Python',
          'Topic :: Software Development :: Testing',
    ],
    keywords='robotframework historical execution report parser',
    author='Shiva Prasad Adirala',
    author_email='adiralashiva8@gmail.com',
    url='https://github.com/adiralashiva8/robotframework-historic-parser',
    license='MIT',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=REQUIREMENTS,
    entry_points={
        'console_scripts': [
          'rfhistoricparser=robotframework_historic_parser.parserargs:main',
        ]
    },
)
