"""
Buildout recipe for generating files from Jinja2 templates.
"""

__author__ = "Torgeir Lorange Ostby <torgeilo@gmail.com>"
__version__ = "2.0"


import os
import re
import sys
import logging
import jinja2

from zc.buildout import UserError
from zc.recipe.egg.egg import Eggs

from amplecode.recipe.template.filters import split
from amplecode.recipe.template.filters import default_filters


log = logging.getLogger(__name__)


class Recipe(object):
    """
    Buildout recipe for making files out of Jinja2 templates. All part options
    are directly available to the template. In addition, the properties of all
    other parts are available through parts.<part>.<key>.

    If an eggs option is defined, then the egg references are transformed into
    a pkg_resources.WorkingSet object before given to the template.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

    def update(self):
        """
        Recipe update function. Does the same as install.
        """

        return self.install()

    def install(self):
        """
        Recipe install function.
        """

        # The root directory is absolute or relative to the buildout root
        root = self.options.get("root", ".")
        if not os.path.isabs(root):
            root = os.path.abspath(os.path.join(
                    self.buildout["buildout"]["directory"], root))

        # Parse the templates option
        p = re.compile(r"(\".+\"|\S+)\s+(\".+\"|\S+)(?:\s+mode=(\d+))?")
        templates = p.findall(self.options.get("templates", ""))
        if not templates:
            log.warning("No templates specified")

        # Configure the template environments
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(root))
        env.filters.update(self._load_filters())
        context = self._create_context()

        for template in templates:
            self._render(root, env, context, *template)

        return self.options.created()

    def _render(self, root, env, context, template_file, target_file, mode):
        """
        Render the given template, save, and set the mode. Create any target
        directories, if necessary.
        """

        template_file = template_file.strip('"')
        target_file = target_file.strip('"')

        log.info(template_file + " -> " + target_file +
                 (", mode=" + mode if mode else ""))

        try:
            template = env.get_template(template_file)
        except jinja2.TemplateNotFound, e:
            log.error("Could not find the template file: %s" % e.name)
            raise UserError("Template file not found: %s" % e.name)

        if not os.path.isabs(target_file):
            target_file = os.path.join(root, target_file)

        target_dir = os.path.dirname(target_file)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        output = template.render(**context)

        fp = open(target_file, "wt")
        fp.write(output)
        fp.close()

        if mode:
            os.chmod(target_file, int(mode, 8))

        self.options.created(target_file)

    def _create_context(self):
        """
        The template context contains the local options, a reference to the
        other parts, and potentially a list of eggs.
        """

        context = dict((k, v.strip()) for k, v in self.options.iteritems())

        if 'parts' in context.keys():
            log.error("You cannot not use 'parts' as variable name. It is "
                      "reserved for providing accessing to the other parts of "
                      "the buildout.")
            raise UserError("parts used as a variable in %s" % self.name)

        context.update({'parts': self.buildout})

        if "eggs" in context:
            log.info("Making working set out of the eggs")
            eggs = Eggs(self.buildout, self.options["recipe"], self.options)
            _names, eggs = eggs.working_set()
            context["eggs"] = eggs

        return context

    def _load_filters(self):
        """
        Create a dict of template filters. Add the default filters and load any
        filter libraries listed in the options.
        """

        filters = {}
        filters.update(default_filters)

        modules = split(self.options.get("filters", ""))

        for module in modules:
            log.info("Loading filters from " + module)
            __import__(module)
            filters.update(sys.modules[module].filters)

        return filters
