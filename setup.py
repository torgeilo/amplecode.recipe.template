from setuptools import setup, find_packages

setup(
    name='amplecode.recipe.template',
    version='1.0.0',
    packages=find_packages(),
    namespace_packages=['amplecode', 'amplecode.recipe'],
    install_requires=['setuptools', 'zc.recipe.egg', 'Jinja2'],
    zip_safe=True,
    entry_points="""
        [zc.buildout]
        default = amplecode.recipe.template:Recipe
    """,
)
