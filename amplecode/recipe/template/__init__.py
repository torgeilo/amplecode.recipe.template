"""
Buildout template recipe using Jinja2.
"""

__author__ = 'Torgeir Lorange Ostby <torgeilo@gmail.com>'
__version__ = '1.0'
__license__ = """
Copyright (c) 2008, Torgeir Lorange Ostby <torgeilo@gmail.com>.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the AmpleCode project nor the names of its
      contributors may be used to endorse or promote products derived from
      this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

import os
import logging
import jinja2
import zc.buildout
from zc.recipe.egg.egg import Eggs


log = logging.getLogger(__name__)


class Recipe(object):
    """
    Template recipe using Jinja2. All part options are available to the
    template.

    If an eggs option is defined, the egg references are transformed into a
    pkg_resources.WorkingSet object before given to the template.

    If an option contains multiple lines it is turned into a list of stripped
    strings before given to the template.
    """

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        if not "template-file" in options:
            log.error("You need to specify a template-file")
            raise zc.buildout.UserError("No template file specified")
        if not "target-file" in options:
            log.error("You need to specify a target-file")
            raise zc.buildout.UserError("No target file specified")

    def install(self):
        non_string_options = dict()

        # Strip options
        for key, value in self.options.iteritems():
            self.options[key] = value.strip()

        # Make eggs available to template if specified
        if "eggs" in self.options:
            log.info("Making working set out of the eggs")
            eggs = Eggs(self.buildout, self.options["recipe"], self.options)
            names, eggs = eggs.working_set()
            non_string_options['eggs'] = eggs
            del self.options['eggs']

        # Handle lists
        for key, value in self.options.iteritems():
            if key == "eggs":
                continue
            if "\n" in value.strip():
                log.info("Making list out of option %r" % key)
                value = [line.strip() for line in value.split("\n")
                         if line.strip()]
                non_string_options[key] = value
                del self.options[key]

        # Check template and target lists
        template_files = non_string_options.get("template-file",
                [self.options.get("template-file")])
        target_files = non_string_options.get("target-file",
                [self.options.get("target-file")])
        if len(template_files) != len(target_files):
            raise zc.buildout.UserError(
                    "The number of template and target files must match")
        target_executables = non_string_options.get("target-executable",
                [self.options.get("target-executable", "false")])
        if len(target_executables) > 1:
            if len(target_executables) != len(template_files):
                raise zc.buildout.UserError("The number of target executables"
                        "must 0, 1 or match the number of template files")
            target_executables = [value.lower() in ('yes', 'true', '1')
                                  for value in target_executables]
        else:
            value = target_executables[0].lower() in ('yes', 'true', '1')
            target_executables = [value for i in xrange(len(template_files))]
        files = zip(template_files, target_files, target_executables)

        # Set up jinja2 environment
        base = os.path.abspath(os.path.join(self.buildout["buildout"]["directory"],
                                            self.options.get("base-dir", "")))
        jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(base))
        jinja2_env.tests['iterable'] = lambda x: hasattr(x, '__iter__')

        for template_file, target_file, executable in files:
            # Load template
            template = None
            try:
                template = jinja2_env.get_template(template_file)
            except jinja2.TemplateNotFound, e:
                log.error("Could not find the template file: %s" % e.name)
                raise zc.buildout.UserError("Template file not found: %s" % e.name)

            # Render template
            output = template.render(non_string_options, **dict(self.options))

            # Make target file
            target_file = os.path.abspath(target_file)
            directory = os.path.dirname(target_file)
            if not os.path.exists(directory):
                os.mkdir(directory)
                self.options.created(directory)

            fp = open(target_file, "wt")
            fp.write(output)
            fp.close()

            # Chmod target file
            if executable:
                os.chmod(target_file, 0755)
            self.options.created(target_file)

        return self.options.created()

    def update(self):
        self.install()
