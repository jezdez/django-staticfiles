from django.core.management.base import LabelCommand
from staticfiles import resolvers
import os
import sys


class Command(LabelCommand):
    help = "Finds the absolute path for the given static file."
    args = "[static_file]"
    label = 'static file'

    def handle_label(self, media_path, **options):
        paths = resolvers.resolve(media_path, all=True)
        if not paths:
            print "No matching file found."
        else:
            for path in paths:
                print os.path.realpath(path)
