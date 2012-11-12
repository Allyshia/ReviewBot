import os

from reviewbot.tools.process import execute
from reviewbot.tools import Tool

class JSLintTool(Tool):
    name = 'JSLint Code Quality Tool'
    version = '0.1'
    description = "Checks syntax errors and validates JavaScript using the JSLint tool."
    options = [
        {
            'name': 'debug',
            'field_type': 'django.forms.BooleanField',
            'default': False,
            'field_options': {
                'label': 'Debug Enabled',
                'help_text': 'Allow debugger statements',
                'required': False,
            },
        },
        {
            'name': 'devel',
            'field_type': 'django.forms.BooleanField',
            'default': False,
            'field_options': {
                'label': 'Logging Enabled',
                'help_text': 'Allow logging (console, alert, etc.)',
                'required': False,
            },
        },
        {
            'name': 'es5',
            'field_type': 'django.forms.BooleanField',
            'default': False,
            'field_options': {
                'label': 'ECMAScript 5th ed.',
                'help_text': 'Allow ES5 syntax',
                'required': False,
            },
        },
        {
            'name': 'evil',
            'field_type': 'django.forms.BooleanField',
            'default': False,
            'field_options': {
                'label': 'eval() Tolerance',
                'help_text': 'Allow use of eval() statements',
                'required': False,
            },
        },
        {
            'name': 'indent',
            'field_type': 'django.forms.IntegerField',
            'default': 4,
            'field_options': {
                'label': 'Indent',
                'help_text': 'Indent size',
                'required': True,
            },
        },
        {
            'name': 'maxerr',
            'field_type': 'django.forms.IntegerField',
            'default': 1000,
            'field_options': {
                'label': 'Maximum Errors',
                'help_text': 'Maximum number of errors allowed',
                'required': True,
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
            'default': False,
            'field_options': {
                'label': 'Pass/Fail',
                'help_text': 'Stop scan after first error',
                'required': False,
            },
        },
        {
            'name': 'sloppy',
            'field_type': 'django.forms.BooleanField',
            'default': False,
            'field_options': {
                'label': 'Sloppy',
                'help_text': 'Allow "use strict" pragma to be optional',
                'required': False,
            },
        },
        {
            'name': 'white',
            'field_type': 'django.forms.BooleanField',
            'default': False,
            'field_options': {
                'label': 'Whitespace',
                'help_text': 'Tolerate sloppy whitespace',
                'required': False,
            },
        },
    ]

    def handle_files(self, files):
        # Get path to js script relative to current package
        PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))
        lib_path = os.path.join(PACKAGE_ROOT, 'lib/jslint')
        self.runJSLint_path = os.path.join(lib_path, 'runJSLint.js')
        self.jsLint_path = os.path.join(lib_path, 'jslint.js')

        # Get JSLint options from admin panel ...
        settings_bool_keys = ['debug', 'devel', 'es5', 'evil', 'passfail',
            'sloppy','white']

        settings_num_keys = ['indent', 'maxerr', 'maxlen']

        # ... first set the boolean values ...
        self.jsLintOptions = dict((s, str(self.settings[s]).lower())
                                for s in settings_bool_keys)
        
        # ... then the numeric values.
        for s in settings_num_keys:
            self.jsLintOptions[s] = int(self.settings[s])
        
        super(JSLintTool, self).handle_files(files)

    def handle_file(self, f):
        if not f.dest_file.lower().endswith('.js'):
            # Ignore the file.
            return False

        path = f.get_patched_file_path()
        if not path:
            return False
        output = execute(
            [
                'js',
                '-e',
                "load('%s'); runJSLint('%s', read('%s'), %s);"
                    % (self.runJSLint_path, self.jsLint_path, path,
                        self.jsLintOptions)
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
                # A non-numeral was given in the output; don't use it.
                # There was likely an error in processing the .js file.
                return False
            except:
                return False
        return True