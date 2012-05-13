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
import warnings

from zc.buildout import UserError
from zc.recipe.egg.egg import Eggs

from amplecode.recipe.template.filters import split, as_bool, default_filters


log = logging.getLogger(__name__)
warnings.simplefilter("default")


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

        root_option = "root"
        root_targets = True

        if "template-file" in self.options:
            message = ("The template-file, target-file, target-executable, "
                    "and base-dir options have been deprecated in favor of "
                    "the jobs and root options. See the documentation in the "
                    "README.rst file.")
            warnings.warn(message, DeprecationWarning)

            jobs = self._parse_jobs_old()
            root_option = "base-dir"
            root_targets = False
        elif "jobs" in self.options:
            jobs = self._parse_jobs()
        else:
            log.warning("No jobs option specified. Nothing to do!")
            return

        # The root directory is absolute or relative to the buildout root
        root = self.options.get(root_option, ".")
        if not os.path.isabs(root):
            root = os.path.abspath(os.path.join(
                    self.buildout["buildout"]["directory"], root))

        # Configure the template environments
        env = jinja2.Environment(loader=jinja2.FileSystemLoader(root))
        env.filters.update(self._load_filters())
        context = self._create_context(jobs)

        for job in jobs:
            context["jobs"].current = job
            self._render(root, env, context, root_targets=root_targets, **job)

        return self.options.created()

    def _parse_jobs(self):
        """
        Parse the jobs option.
        """

        p = re.compile(r"(?P<template>\".+?\"|'.+?'|\S+)\s+"
                       r"(?P<target>\".+?\"|'.+?'|\S+)"
                       r"(?:\s+mode=(?P<mode>\d+))?")
        jobs = []
        for match in p.finditer(self.options["jobs"]):
            job = match.groupdict()
            job["template"] = job["template"].strip("\"'")
            job["target"] = job["target"].strip("\"'")
            jobs.append(job)

        return jobs

    def _parse_jobs_old(self):
        """
        Parse the template-file, target-file and target-executable options.
        """

        templates = split(self.options.get("template-file", ""))
        targets = split(self.options.get("target-file", ""))

        if len(templates) != len(targets):
            raise UserError(
                    "The number of template and target files much match")

        executables = split(self.options.get("target-executable", "false"))
        executables = map(as_bool, executables)

        if len(executables) == 1:
            value = executables[0]
            executables = (value for i in xrange(len(templates)))
        elif len(executables) != len(templates):
            raise UserError("The number of target executables must be 0, 1, "
                    "or match the number of template files")

        return [
            {
                "template": template,
                "target": target,
                "mode": "0755" if executable else None,
            }
            for template, target, executable
            in zip(templates, targets, executables)
        ]

    def _render(self, root, env, context, template=None, target=None,
                mode=None, root_targets=True):
        """
        Render the given template, save, and set the mode. Create any target
        directories, if necessary.
        """

        log.debug(template + " -> " + target +
                 (", mode=" + mode if mode else ""))

        try:
            template = env.get_template(template)
        except jinja2.TemplateNotFound, e:
            raise UserError("Template file not found: %s" % e.name)

        if root_targets and not os.path.isabs(target):
            target = os.path.join(root, target)

        target_dir = os.path.dirname(target)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        output = template.render(**context)

        fp = open(target, "wt")
        fp.write(output)
        fp.close()

        if mode:
            os.chmod(target, int(mode, 8))

        self.options.created(target)

    def _create_context(self, jobs):
        """
        The template context contains the local options, a reference to the
        other parts, and potentially a list of eggs.
        """

        class CurrentList(list):
            """
            Custom list class that has a current property as well (that needs
            to be maintained manually).
            """

            def __init__(self, *args, **kwargs):
                super(CurrentList, self).__init__(*args, **kwargs)
                self.current = None

        context = dict((k, v.strip()) for k, v in self.options.iteritems())
        context.update({"parts": self.buildout})
        context.update({"jobs": CurrentList(jobs)})

        if "eggs" in context:
            log.debug("Making working set out of the eggs")
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
            log.debug("Loading filters from " + module)
            __import__(module)
            filters.update(sys.modules[module].filters)

        return filters
