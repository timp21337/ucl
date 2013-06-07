#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ucl.settings")

    from django.core.management import execute_from_command_line


    # hack to prevent admin prompt
    if 'syncdb' in sys.argv:
        sys.argv.append('--noinput')

    execute_from_command_line(sys.argv)

