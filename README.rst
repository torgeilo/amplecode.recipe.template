=========================
amplecode.recipe.template
=========================

amplecode.recipe.template is a Buildout recipe for generating files using Jinja2 templates. The recipe configures a Jinja2 environment, by default relative to the Buildout directory, allowing templates to extend and include other templates relative to the environment. 

Downloads are available from pypi: http://pypi.python.org/pypi/amplecode.recipe.template/

Buildout Options
================

* template-file (required): One or more Jinja2 template file paths. 
* target-file (required): One of more target file paths. The number of files must match the number of template files. 
* base-dir: Base directory of the Jinja2 environment. Template file paths are relative to this directory. Default is the Buildout directory. 
* target-executable: One or more boolean flags (yes|no|true|false|1|0) indicating the executability of the target files. If only one flag is given it is applied to all target files. 
* eggs: Reserved for a list of eggs, conveniently converted into a pkg_resources.WorkingSet when specified 

Additional options are simply forwarded to the templates, and multi-line options are converted into lists of strings first.

Iterables
=========

It is possible for a recipe option to contain one or more values, where in the latter case the values are put in a list before supplied to the templates. To find out if an option value is iterable or not, one can use the iterable test (Jinja2)::

  #!/bin/sh
  {% if values is iterable %}
    {% for value in values %}
       echo "{{ value }}"
    {% endfor %}
  {% else %}
    echo "{{ values }}"
  {% endif %}

Minimal Example
===============

foo.txt is created from foo.txt.jinja2 without any extra options::

  [buildout]
  parts = foo

  [foo]
  recipe = amplecode.recipe.template
  template-file = foo.txt.jinja2
  target-file = foo.txt

Larger Example
==============

foo.txt is created from myapp/foo.txt.jinja2, bar.sh is created from myapp/bar.sh.jinja2, the second will be executable, and both templates can utilize the additional options specified::

  [buildout]
  parts = foo

  [foo]
  recipe = amplecode.recipe.template
  base-dir = myapp
  template-file =
      foo.txt.jinja2
      bar.sh.jinja2
  target-file =
      foo.txt
      bar.sh
  target-executable =
      false
      true
  project_name = Another Example
  author = Me

Changelog
=========

See the CHANGELOG file

License
=======

See the LICENSE file
