import os, stat, os.path, getpass, argparse

from django.core import management


parser = argparse.ArgumentParser(
    description = "Start a new Mohawk Django project.",
)
parser.add_argument("project_name",
    help = "The name of the project to create.",
)
parser.add_argument("dest_dir",
    default = None,
    nargs = "?",
    help = "The destination dir for the created project.",
)
parser.add_argument("--noinput", 
    action = "store_false",
    default = True,
    dest = "interactive",
    help = "Tells Django to NOT prompt the user for input of any kind.",
)


def make_executable(path):
    st = os.stat(path)
    os.chmod(path, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def main():
    args = parser.parse_args()
    dest_dir = args.dest_dir or args.project_name
    # Create the project.
    try:
        os.makedirs(dest_dir)
    except OSError:
        pass
    management.call_command("startproject",
        args.project_name,
        dest_dir,
        template = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "project_template")),
        extensions = ("py", "txt", "conf", "gitignore", "md", "css", "js"),
        user = getpass.getuser(),
        project_slug = args.project_name.replace("_", "-"),
    )
    # Make management scripts executable.
    make_executable(os.path.join(dest_dir, "manage.py"))
    # Give some help to the user.
    print "etianen-cms project created."
