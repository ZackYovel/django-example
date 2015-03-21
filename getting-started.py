import os

"""
This script scans it's directory and subdirectories to find comments starting whth '# GETTING-STARTED:'.
It prints every such comment (and it's containing file and line number), to create a list of GETTING-STARTED comments.
Leave your GETTING-STARTED notes wherever you need them, than run this script to print them all.
When a GETTING-STARTED item is no longer needed, "hide" it from this script by commenting it out,
changing any of it's tag letters (# GETTING-STARTED:) or just delete it. 
"""
# For example, delete one '#' form the start of the next line to have it printed when running this script:
## GETTING-STARTED: make sure to run the getting-started.py script when you start a new project or deploy one.
# Now hide it again by adding the '#' back.

def find_getting_started_comments_recursively(path):
	for root, subdirectories, files in os.walk(path):
		for f in files:
			line_counter = 1
			relative_file = os.path.join(root, f)
			for line in open(relative_file):
				if line.startswith("# GETTING-STARTED:"):
					print(relative_file + " line " + str(line_counter) + ":\n" + line)
				line_counter += 1

find_getting_started_comments_recursively('.')