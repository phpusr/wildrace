#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def change_app_directory(directory):
    cur_path = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(cur_path, directory)
    sys.path.append(app_path)
    os.chdir(app_path)


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    change_app_directory('backend')
    main()
