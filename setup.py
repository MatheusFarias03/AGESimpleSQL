from setuptools import setup, find_packages

setup(
    name="age_simple_sql",
    version="0.3",
    packages=find_packages(),
    install_requires=[
        'psycopg2-binary'
    ],
    author="Matheus Farias de Oliveira Matsumoto",
    description="A simple SQL wrapper for Apache AGE using psycopg2 connection pooling.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MatheusFarias03/AGESimpleSQL"
)