from reviewbot.tools.process import execute
from reviewbot.tools import Tool


class JSLintTool(Tool):
    name = 'JSLint Style Checker'
    version = '1.0'
    description = "Checks JavaScript code for style errors using the JSLint tool."
    

    def handle_file(self, f):
        if not f.dest_file.endswith('.js'):
            # Ignore the file.
            return False

        path = f.get_patched_file_path()
        if not path:
            return False

        output = execute(
            [
                'js',
                '-e',
                "load('runJSLint.js'); runJSLint(read('%s'))" % path
            ],
            split_lines=True,
            ignore_errors=True)

        for line in output:
            parsed = line.split(':')
            lnum = int(parsed[1])
            col = int(parsed[2])
            msg = parsed[3]
            f.comment('Col: %s\n%s' % (col, msg), lnum)

        return True