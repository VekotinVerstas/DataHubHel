#!/usr/bin/env python
import os
import sys

import django.core.management

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "datahubhel.settings")
    django.core.management.execute_from_command_line(sys.argv)
