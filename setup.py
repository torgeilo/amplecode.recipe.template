from setuptools import setup, find_packages

setup(
    name='amplecode.recipe.template',
    version='0.1.1',

    author='Torgeir Lorange Ostby',
    author_email='torgeilo@gmail.com',
    description='Buildout template recipe using Jinja2',
    keywords='Buildout recipe template Jinja2',
    license='BSD',
    url='http://amplecode.org/',

    packages=find_packages(),
    namespace_packages=['amplecode', 'amplecode.recipe'],
    install_requires=['setuptools', 'zc.recipe.egg', 'Jinja2'],
    zip_safe=True,
    entry_points="""
        [zc.buildout]
        default = amplecode.recipe.template:Recipe
    """,
)
