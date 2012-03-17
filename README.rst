=========================
amplecode.recipe.template
=========================

amplecode.recipe.template is a Buildout recipe for generating files using Jinja2 templates. The recipe configures a Jinja2 environment, by default relative to the Buildout directory, allowing templates to extend and include other templates relative to the environment.

Downloads are available from pypi: http://pypi.python.org/pypi/amplecode.recipe.template/

Buildout Options
================

* templates: A list of template paths, output file paths, and potentially file modes. The different elements can be separated by any kind of whitespace. Paths containing whitespace can be enclosed in double quotes. Please see the examples below.
* filters: A list of template filter libraries. The libraries must be python modules containing a ``filters`` attribute, holding a dictionary of filter names and functions. The filters are loaded in order, potentially overriding any previous filters with same names.
* root: Base directory of the Jinja2 environment, and the root of all template and relative file paths. Default is the Buildout directory.
* eggs: Reserved for a list of eggs, conveniently converted into a ``pkg_resources.WorkingSet`` when specified.

Additional options are simply forwarded to the templates, and options from all the other parts are made available through ``parts.<part-name>.<option-name>`` and ``parts[<part-name>][<option-name>]``.

Minimal Example
===============

foo.txt is created from foo.txt.jinja2 without any extra options::

  [buildout]
  parts = foo

  [foo]
  recipe = amplecode.recipe.template
  templates = foo.txt.jinja2 foo.txt

Larger Example
==============

foo.txt is created from myapp/foo.txt.jinja2, bar.sh is created from myapp/bar.sh.jinja2, the second will be executable, and both templates can utilize the additional options and template filters::

  [buildout]
  parts = foo

  [foo]
  recipe = amplecode.recipe.template
  filters =
      my.custom,filters
      another.filter.module
  root = myapp
  templates =
      foo.txt.jinja2 foo.txt
      bar.sh.jinja2 bar.sh mode=0775
  project_name = Another Example
  author = Me

The mode value must be octal, as supported by ``os.chmod``.

Any kind of whitespace is allowed between the elements in the templates option, including line breaks. No whitespace is allowed in the mode argument. The above example could very well be written as::

  [buildout]
  parts = foo

  [foo]
  recipe = amplecode.recipe.template
  root = myapp
  filters =
      my.custom,filters
      another.filter.module
  templates =
      foo.txt.jinja2
      foo.txt

      bar.sh.jinja2
      bar.sh
      mode=0775
  project_name = Another Example
  author = Me

If a path contains spaces, it can be enclosed in double quotes (").

Lists of Values
===============

If you want to iterate over a whitespace-separated list of values, provided in a single option, you can use the split filter, available by default. For example, if your buildout.cfg contains::

  ...
  words = Hello world!
  ...

you can use it in your Jinja2 template like::

  #!/bin/sh
  {% for word in words|split %}
     echo "{{ word }}"
  {% endfor %}

Changelog
=========

See the CHANGELOG file

License
=======

See the LICENSE file
