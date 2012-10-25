from reviewbot.tools.process import execute
from reviewbot.tools import Tool
import os

class JSLintTool(Tool):
    name = 'JSLint Code Quality Tool'
    version = '0.1'
    description = "Checks syntax errors and validates JavaScript using the JSLint tool."

    options = [
        {
            'name': 'debug',
            'field_type': 'django.forms.BooleanField',
            'default': True,
            'field_options': {
                'label': 'Debug Enabled',
                'help_text': 'Allow debugger statements',
                'required': False,
            },
        },
        {
            'name': 'devel',
            'field_type': 'django.forms.BooleanField',
            'default': True,
            'field_options': {
                'label': 'Logging Enabled',
                'help_text': 'Allow logging (console, alert, etc.)',
                'required': False,
            },
        },
        {
            'name': 'es5',
            'field_type': 'django.forms.BooleanField',
            'default': True,
            'field_options': {
                'label': 'ECMAScript 5th ed.',
                'help_text': 'Allow ES5 syntax',
                'required': False,
            },
        },
        {
            'name': 'evil',
            'field_type': 'django.forms.BooleanField',
            'default': True,
            'field_options': {
                'label': 'eval() Tolerance',
                'help_text': 'Allow use of eval() statements',
                'required': False,
            },
        },
        {
            'name': 'maxlen',
            'field_type': 'django.forms.IntegerField',
            'default': 79,
            'field_options': {
                'label': 'Maximum Line Length',
                'help_text': 'Maximum source line length allowed',
                'required': True,
            },
        },
        {
            'name': 'passfail',
            'field_type': 'django.forms.BooleanField',
            'default': True,
            'field_options': {
                'label': 'Pass/Fail',
                'help_text': 'Stop scan after first error',
                'required': False,
            },
        },
        {
            'name': 'sloppy',
            'field_type': 'django.forms.BooleanField',
            'default': True,
            'field_options': {
                'label': 'Sloppy',
                'help_text': 'Allow "use strict" pragma to be optional',
                'required': False,
            },
        },
        {
            'name': 'white',
            'field_type': 'django.forms.BooleanField',
            'default': True,
            'field_options': {
                'label': 'whitespace',
                'help_text': 'Tolerate sloppy whitespace',
                'required': False,
            },
        },
    ]

    def handle_file(self, f):
        if not f.dest_file.lower().endswith('.js'):
            # Ignore the file.
            return False

        path = f.get_patched_file_path()
        if not path:
            return False

        #Get path to js script relative to current package
        PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
        lib_path = os.path.join(PACKAGE_ROOT, 'lib')
        runJSLint_path = os.path.join(lib_path, 'runJSLint.js')
        jsLint_path = os.path.join(lib_path, 'jslint.js')

        jsLintOptions = {
            'debug' : str(self.settings['debug']).lower(),
            'devel' : str(self.settings['devel']).lower(),
            'es5' : str(self.settings['es5']).lower(),
            'evil' : str(self.settings['evil']).lower(),
            'maxlen' : int(self.settings['maxlen']),
            'passfail' : str(self.settings['passfail']).lower(),
            'sloppy' : str(self.settings['sloppy']).lower(),
            'white' : str(self.settings['white']).lower(),
        }

        output = execute(
            [
                'js',
                '-e',
                "load('%s'); runJSLint('%s', read('%s'), %s);"
                    % (runJSLint_path, jsLint_path, path, jsLintOptions)
            ],
            split_lines=True,
            ignore_errors=True)

        for line in output:
            try:
                parsed = line.split(':')
                lnum = int(parsed[0])
                col = int(parsed[1])
                msg = parsed[2]
                f.comment('Col: %s\n%s' % (col, msg), lnum)
            except ValueError:
                # non-numeral was given in the output; don't use it.
                return False

        return True