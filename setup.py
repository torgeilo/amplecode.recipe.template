from setuptools import setup, find_packages

setup(
    name='amplecode.recipe.template',
    version='1.0',

    author='Torgeir Lorange Ostby',
    author_email='torgeilo@gmail.com',
    description='Buildout recipe for making files out of Jinja2 templates',
    keywords='Buildout recipe template Jinja2',
    license='BSD',
    url='http://www.amplecode.org/',

    packages=find_packages(),
    namespace_packages=['amplecode', 'amplecode.recipe'],
    install_requires=['setuptools', 'zc.recipe.egg', 'Jinja2'],
    zip_safe=True,
    entry_points="""
        [zc.buildout]
        default = amplecode.recipe.template:Recipe
    """,
)
