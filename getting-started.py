import os

"""
This script scans it's directory and subdirectories to find comments starting whth '# GETTING-STARTED:'.
It prints every such comment (and it's containing file and line number),
And lets you choose if you want to hide it before moving to the next.
Leave your GETTING-STARTED notes wherever you need them, than run this script to print them all.
When a GETTING-STARTED item is no longer needed, "hide" it from this script by commenting it out,
changing any of it's tag letters (# GETTING-STARTED:) or just delete it. 
"""
# For example, delete one '#' form the start of the next line to have it printed when running this script:
# GETTING-STARTED: make sure to run the getting-started.py script when you start a new project or deploy one.
# Now hide it again by adding the '#' back.

class GettingStartedManager:
    FORMAT = "# GETTING-STARTED:"
    changes = {}

    def __init__(self, change=False, hidden=False, select_all=False,
                 hide_all=False, unhide_all=False,
                 remove_un_hidden=False, remove_hidden=False, remove_all=False,
                 paths=('.'), prefix='#'):
        """Create a new GettingStartedManager, targeting the given path."""
        self._change = change
        self._hidden = hidden
        self._hide_all = hide_all
        self._unhide_all = unhide_all
        self._remove_un_hidden = remove_un_hidden
        self._remove_hidden = remove_hidden
        self._remove_all = remove_all
        self._paths = paths

        # general cases
        self._select_all = select_all or remove_all
        self._hidden_mode = hidden or unhide_all or remove_hidden

        # formats to use (hidden and unhidden)
        self._formats = []
        if select_all or not self._hidden_mode:
            self._formats.append(self.FORMAT)
        if select_all or self._hidden_mode:
            self._formats.append(prefix + self.FORMAT)

        # change mode: is this GSM allowed to write changes.
        self._change_mode = any((
            self._change, self._hide_all, self._unhide_all,
            self._remove_un_hidden,
            self._remove_hidden, self._remove_all
        ))

        self._batch_mode = any((
            self._select_all, self._hide_all, self._unhide_all,
            self._remove_hidden,
            self._remove_un_hidden
        ))

    def is_hidden(self, comment):
        return not comment.startswith(self.FORMAT)

    @property
    def hidden_mode(self):
        return self._hidden_mode

    @property
    def change_mode(self):
        return self._change_mode

    @property
    def batch_mode(self):
        return self._batch_mode

    def set_change(self, file_name, line_number, new_line):
        if self._change_mode:
            if file_name not in self.changes:
                self.changes[file_name] = []
            self.changes[file_name].append((line_number, new_line))

    def comments(self):
        # for every file in every path
        for path in self._paths:
            if os.path.isdir(path):
                for root, f in (files for root, s, files in os.walk(path)):
                    return self.process_file(root, f)
            else:
                return self.process_file('', path)


    def write(self):
        if self._change_mode:
            for file_name in self.changes:
                with open(file_name) as f:
                    lines = f.readlines()
                    for line_number, new_line in self.changes[file_name]:
                        lines[line_number] = new_line + "/n"
                with open(file_name, 'w') as f:
                    f.writelines(lines)

    def process_file(self, root, f):
        line_counter = 1
        relative_file = os.path.join(root, f)
        for line in open(relative_file):
            line = line.strip()
            if (line.startswith(fmt) for fmt in self._formats):
                yield (relative_file, line_counter, line)
            line_counter += 1


if __name__ == "__main__":
    from sys import argv

    USAGE = """
usage: getting-started.py [arg1[ arg2]]

options:
    -H, --help
        print this message and exit (default for unknowen arguments).
    
    -c, --change
        scan directory in write mode, and allow the user to hide each
        comment.
    
    -h, --hidden
        searches for hidden comments instead of un-hidden ones.
        If the -c/--change arg was also sent, the user will be
        prompted with the option to un-hide each hidden comment.
        NOTICE: this option only tracks comments that have been
        pre-fixed with a '#' (such as
            '## GETTING-STARTED: do something')
        comments hidden by the script are compatible with this
        format and will be displayed when this arg is sent.

    -ha --hide-all
        search and hide all comments, do not prompt user.

    -ua --unhide-all
        search and unhide all hidden comments, do not prompt user.

    -ra --remove-all
        search and remove all comments (or all hidden comments if
        the -h or --hidden flags are present)
"""

    change = False
    hidden = False
    select_all = False
    hide_all = False
    unhide_all = False
    remove_un_hidden = False
    remove_hidden = False
    remove_all = False
    paths = ('.',)
    prefix = '#'

    arg = None
    try:
        for arg in argv:
            if arg is None or arg.endswith('getting-started.py'):
                pass
            elif arg in {'-pr', '--prefix'}:
                i = argv.index(arg) + 1
                prefix = argv[i]
                argv[i] = None
            elif arg in {'-p', '--paths'}:
                i = argv.index(arg) + 1
                paths = argv[i].split(";")
                argv[i] = None
            elif arg in ('-ra', '--remove-all'):
                remove_all = True
            elif arg in ('-ha', '--hide-all'):
                hide_all = True
            elif arg in ('-rmh', '--remove-hidden'):
                remove_hidden = True
            elif arg in ('-rmuh', '--remove-unhidden'):
                remove_un_hidden = True
            elif arg in ('-ua', '--unhide-all'):
                unhide_all = True
            elif arg in ('-sa', '--select_all'):
                select_all = True
            elif arg in ('-h', '--hidden'):
                hidden = True
            elif arg in ('-c', '--chage'):
                change = True
            else:
                print USAGE
                exit(0)
    except IndexError as ie:
        if arg in {'-pr', '--prefix'} and paths == ('.',):
            print """
usage:
    getting-started.py [arg1[arg2[...]]] -pr <str> [more_arg1[more_arg2[...]]]

A prefix token must be sent as the next argument.
"""
        if arg in {'-p', '--paths'} and prefix == '#':
            print """
usage:
    getting-started.py [arg1[arg2[...]]] -p <;-separated-list> [more_arg1[more_arg2[...]]]

A smi-colon separated list of paths mush be sent as the next argument.
"""
        exit(1)

    gsm = GettingStartedManager(
        change=change, hidden=hidden, select_all=select_all, hide_all=hide_all,
        unhide_all=unhide_all, remove_un_hidden=remove_un_hidden,
        remove_hidden=remove_hidden, remove_all=remove_all, paths=paths,
        prefix=prefix
    )

    if not gsm.batch_mode:
        for relative_file, line_number, line in gsm.comments():
            print(relative_file + " line " + str(line_number) + ":\n" + line)
            if gsm.change_mode:
                if gsm.is_hidden(line):
                    action = raw_input("skip/unhide/remove? [skip]")
                else:
                    action = raw_input("skip/hide/remove? [skip]:")
            else:
                action = raw_input("next?")

            if gsm.change_mode:
                if not relative_file in gsm.changes:
                    gsm.changes[relative_file] = []
                if unhide_all or not gsm.batch_mode and action in {'u',
                                                                   'un-hide',
                                                                   'unhide',
                                                                   "un hide"}:
                    change = line[1:]
                elif hide_all or not gsm.batch_mode and action in {'hide',
                                                                   'h'}:
                    change = '#' + line
                elif remove_all or not gsm.batch_mode and action in {'r',
                                                                     'remove'}:
                    change = ''
                else:
                    print "unknowen action: " + action
                gsm.set_change(relative_file, line_number, change)

    gsm.write()
