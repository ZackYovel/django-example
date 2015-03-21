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

def find_getting_started_comments(path, prefix=''):
    for root, subdirectories, files in os.walk(path):
        for f in files:
            line_counter = 1
            relative_file = os.path.join(root, f)
            for line in open(relative_file):
                line = line.strip()
                if line.startswith(prefix + "# GETTING-STARTED:"):
                    yield (relative_file, line_counter, line)
                line_counter += 1


if __name__ == "__main__":
    from sys import argv
    import re

    USAGE ="""
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
"""

    change_mode = False
    hidden_mode = False
    hide_all = False
    unhide_all = False

    for arg in argv:
        if arg.endswith('getting-started.py'):
            pass
        elif arg in ('-ha', '--hide_all'):
            hide_all = True
        elif arg in ('-ua', '--unhide_all'):
            unhide_all = True
        elif arg in ('-h', '--hidden'):
            hidden_mode = True
        elif arg in ('-c','--chage'):
            change_mode = True
        else:
            print USAGE
            exit(0)

    all_mode = hide_all or unhide_all

    # (un)hide-all=True impicitly means change_mode=True, but not the other way.
    if all_mode:
        change_mode = True

    files = {}

    prefix = '#' if hidden_mode or unhide_all else ''
    for relative_file, line_number, line in find_getting_started_comments('.', prefix):
        if not all_mode:
            print(relative_file + " line " + str(line_number) + ":\n" + line)

        if not all_mode:
            if change_mode:
                if hidden_mode:
                    action = raw_input("skip/un-hide? [skip]:")
                else:
                    action = raw_input("skip/hide? [skip]:")
            else:
                action = raw_input("next?")

        if change_mode:
            if not relative_file in files:
                files[relative_file] = []
            if unhide_all or not all_mode and action in {'u', 'un-hide', 'unhide'}:
                change = line[1:]
            elif hide_all or not all_mode and action in {'hide', 'h'}:
                change = ('#' + line)
            else:
                print "unknowen action: " + action
            files[relative_file] += [(line_number, change)]

    if change_mode:
        for path in files:
            changes = files[path]
            with open(path) as f:
                lines = f.readlines()
                for change in changes:
                    lines[change[0]-1] = change[1] + "\n"
            with open(path, 'w') as f:
                f.writelines(lines)
