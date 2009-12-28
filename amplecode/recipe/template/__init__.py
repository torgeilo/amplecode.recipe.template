"""
Buildout recipe for making files out of Jinja2 templates.
"""

__author__ = 'Torgeir Lorange Ostby <torgeilo@gmail.com>'
__version__ = '1.1'

import os
import re
import logging

import jinja2
import zc.buildout
from zc.recipe.egg.egg import Eggs


log = logging.getLogger(__name__)


class Recipe(object):
    """
    Buildout recipe for making files out of Jinja2 templates. All part options
    are directly available to the template. In addition, all options from all
    parts listed in the buildout section pluss the options from the buildout
    section itself are available to the templates through parts.<part>.<key>.

    If an eggs option is defined, the egg references are transformed into a
    pkg_resources.WorkingSet object before given to the template.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        # Validate presence of required options
        if not "template-file" in options:
            log.error("You need to specify a template-file")
            raise zc.buildout.UserError("No template file specified")
        if not "target-file" in options:
            log.error("You need to specify a target-file")
            raise zc.buildout.UserError("No target file specified")

    def install(self):
        """
        Recipe install function.
        """

        # Helper functions

        def split(s):
            """
            Template filter splitting on any whitespace.
            """

            return re.split("\s+", s.strip())

        def as_bool(s):
            """
            Template filter which translates the given string into a boolean.
            """

            return s.lower() in ("yes", "true", "1", "on")

        def strip_dict(d):
            """
            Strips the values of a dictionary in place. All values are assumed
            to be strings. The same dictionary object is returned.
            """

            for k, v in d.iteritems():
                d[k] = v.strip()
            return d

        # Validate template and target lists
        template_files = split(self.options["template-file"])
        target_files = split(self.options["target-file"])
        if len(template_files) != len(target_files):
            raise zc.buildout.UserError(
                    "The number of template and target files must match")

        # Validate and normalise target executable option
        target_executables = split(self.options.get("target-executable",
                                                    "false"))
        target_executables = [as_bool(v) for v in target_executables]
        if len(target_executables) == 1:
            value = target_executables[0]
            target_executables = (value for i in xrange(len(template_files)))
        else:
            if len(target_executables) != len(template_files):
                raise zc.buildout.UserError("The number of target executables"
                        "must 0, 1 or match the number of template files")

        # Assemble lists
        files = zip(template_files, target_files, target_executables)

        # Assemble template context
        context = strip_dict(dict(self.options))

        # Handle eggs specially
        if "eggs" in context:
            log.info("Making working set out of the eggs")
            eggs = Eggs(self.buildout, self.options["recipe"], self.options)
            names, eggs = eggs.working_set()
            context["eggs"] = eggs

        # Make options from other parts available. The parts include the
        # buildout part and all parts specified in the buildout part.
        part_options = {}
        for part in ['buildout'] + split(self.buildout["buildout"]["parts"]):
            part_options[part] = strip_dict(dict(self.buildout[part].items()))
        if 'parts' not in context.keys():
            context.update({'parts': part_options})
        else:
            log.error("You should not use parts as a name of a variable,"
                      " since it is used internally by this receipe")
            raise zc.buildout.UserError("parts used as a variable in %s"
                                        % self.name)

        # Set up jinja2 environment
        jinja2_env = self._jinja2_env(filters={
            "split": split,
            "as_bool": as_bool,
            "type": type,
        })

        # Load, render, and save files
        for template_file, target_file, executable in files:
            template = self._load_template(jinja2_env, template_file)
            output = template.render(**context)

            # Make target file
            target_file = os.path.abspath(target_file)
            self._ensure_dir(os.path.dirname(target_file))

            fp = open(target_file, "wt")
            fp.write(output)
            fp.close()

            # Chmod target file
            if executable:
                os.chmod(target_file, 0755)

            self.options.created(target_file)

        return self.options.created()

    def update(self):
        """
        Recipe update function. Does the same as install.
        """

        self.install()

    def _jinja2_env(self, filters=None):
        """
        Creates a Jinja2 environment.
        """

        base = os.path.abspath(os.path.join(
                self.buildout["buildout"]["directory"],
                self.options.get("base-dir", "")))
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(base))
        if filters:
            env.filters.update(filters)
        return env

    def _load_template(self, env, path):
        """
        Tried to load the Jinja2 template given by the environment and
        template path.
        """

        try:
            return env.get_template(path)
        except jinja2.TemplateNotFound, e:
            log.error("Could not find the template file: %s" % e.name)
            raise zc.buildout.UserError("Template file not found: %s" % e.name)

    def _ensure_dir(self, directory):
        """
        Ensures that the specified directory exists.
        """

        if not os.path.exists(directory):
            os.mkdir(directory)
            self.options.created(directory)
