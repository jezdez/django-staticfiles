from django.core.management.base import LabelCommand
from staticfiles import resolvers
from staticfiles.management.base import CommandLogger
from optparse import make_option
import os


class Command(CommandLogger, LabelCommand):
    help = "Finds the absolute paths for the given static file(s)."
    args = "[static_file ...]"
    label = 'static file'
    option_list = LabelCommand.option_list + (
        make_option('--first', action='store_false', dest='all', default=True,
                    help="Only return the first match for each static file."),
    )

    def handle_label(self, media_path, **options):
        logger = self.get_logger()
        all = options['all']
        match = resolvers.resolve(media_path, all=all)
        if not match:
            logger.warning("No matching file found for %r." % media_path)
        if all:
            match = '\n'.join([os.path.realpath(path) for path in match])
        return match
