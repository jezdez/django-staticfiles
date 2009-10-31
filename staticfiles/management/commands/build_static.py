import os
import shutil
import sys
from optparse import make_option

from django.core.files.storage import FileSystemStorage
from django.core.management.base import CommandError

from staticfiles.management.base import OptionalAppCommand
from staticfiles.settings import DIRS, STORAGE
from staticfiles import utils

try:
    set
except NameError:
    from sets import Set as set # Python 2.3 fallback


class Command(OptionalAppCommand):
    """
    Command that allows to copy or symlink media files from different
    locations to the settings.STATIC_ROOT.

    Based on the collectmedia management command by Brian Beck:
    http://blog.brianbeck.com/post/50940622/collectmedia
    """
    option_list = OptionalAppCommand.option_list + (
        make_option('--noinput', action='store_false', dest='interactive',
            default=True, help="Do NOT prompt the user for input of any "
                "kind."),
        make_option('-i', '--ignore', action='append',
            default=['CVS', '.*', '*~'], dest='ignore_patterns',
            metavar='PATTERNS', help="A space-delimited list of glob-style "
                "patterns to ignore. Use multiple times to add more."),
        make_option('-n', '--dry-run', action='store_true', dest='dry_run',
            help="Do everything except modify the filesystem."),
        make_option('-l', '--link', action='store_true', dest='link',
            help="Create a symbolic link to each file instead of copying."),
    )
    help = ("Copy static media files from apps and other locations in a "
            "single location.")

    def handle(self, *app_labels, **options):
        ignore_patterns = options['ignore_patterns']
        options['skipped_files'] = []
        options['copied_files'] = []
        storage = utils.dynamic_import(STORAGE)()
        options['destination_storage'] = storage
        try:
            destination_paths = utils.get_files(storage, ignore_patterns)
        except OSError:
            # The destination storage location may not exist yet. It'll get
            # created when the first file is copied.
            destination_paths = []
        options['destination_paths'] = destination_paths
        try:
            storage.path('')
            destination_local = True
        except NotImplementedError:
            destination_local = False
        options['destination_local'] = destination_local
        if options['link']:
            if sys.platform == 'win32':
                message = "Symlinking is not supported by this platform (%s)."
                raise CommandError(message % sys.platform)
            if not destination_local:
                raise CommandError("Can't symlink to a remote destination.")
        # Warn before doing anything more.
        if options.get('interactive'):
            confirm = raw_input("""
You have requested to collate static media files and copy them to the
destination location as specified in your settings file. 

This will overwrite existing files. Are you sure you want to do this?

Type 'yes' to continue, or 'no' to cancel: """)
            if confirm != 'yes':
                raise CommandError("Static files build cancelled.")
        return super(Command, self).handle(*app_labels, **options)

    def pre_handle_apps(self, **options):
        """
        Copy all files from a directory.
        
        """
        ignore_patterns = options['ignore_patterns']
        for prefix, root in DIRS:
            source_storage = FileSystemStorage(location=root)
            for source in self.get_files(source_storage, ignore_patterns):
                self.copy_file(source, prefix, source_storage, **options)

    def post_handle_apps(self, **options):
        copied_files = options['copied_files']
        logger = self.get_logger()
        count = len(copied_files)
        logger.info("%s static file%s built." % (count,
                                                 count != 1 and 's' or ''))

    def handle_app(self, app, **options):
        """
        Copy all static media files from an application.
        
        """
        ignore_patterns = options['ignore_patterns']
        prefix = utils.get_app_prefix(app)
        for storage in utils.app_static_storages(app):
            for path in utils.get_files(storage, ignore_patterns):
                self.copy_file(path, prefix, storage, **options)

    def excluded_app(self, app, **options):
        """
        Gather all the static media files for excluded apps.
        
        This is so a warning can be issued for later copied files which would
        normally be copied by excluded apps.
        
        """
        skipped_files = options['skipped_files']
        ignore_patterns = options['ignore_patterns']
        all_files = utils.get_files_for_app(app, ignore_patterns)
        skipped_files.extend(all_files)

    def copy_file(self, source, destination_prefix, source_storage, **options):
        """
        Attempt to copy (or symlink) `source` to `destination`, returning True
        if successful.
        """
        destination_storage = options['destination_storage']
        dry_run = options['dry_run']
        logger = self.get_logger()
        if destination_prefix:
            destination = '/'.join([destination_prefix, source])
        else:
            destination = source

        if destination in options['copied_files']:
            logger.warning("Skipping duplicate file (already copied earlier):"
                           "\n  %s" % destination)
            return False
        if destination in options['skipped_files']:
            logger.warning("Copying file that would normally be provided by "
                           "an excluded application:\n  %s" % destination)
        source_path = source_storage.path(source)
        if destination in options['destination_paths']:
            if dry_run:
                logger.info("Pretending to delete:\n  %s" % destination)
            else:
                logger.debug("Deleting:\n  %s" % destination)
                destination_storage.delete(destination)
        if options['link']:
            destination_path = destination_storage.path(destination)
            if dry_run:
                logger.info("Pretending to symlink:\n  %s\nto:\n  %s" %
                            (source_path, destination_path))
            else:
                logger.debug("Symlinking:\n  %s\nto:\n  %s" %
                             (source_path, destination_path))
                os.symlink(source_path, destination_path)
        if dry_run:
            logger.info("Pretending to copy:\n  %s\nto:\n  %s" %
                        (source_path, destination))
        else:
            logger.debug("Copying:\n  %s\nto:\n  %s" % (source_path, destination))
            if options['destination_local']:
                destination_path = destination_storage.path(destination)
                try:
                    os.makedirs(os.path.dirname(destination_path))
                except OSError:
                    pass
                shutil.copy2(source_path, destination_path)
            else:
                source_file = source_storage.open(source)
                destination_storage.write(destination, source_file)
        options['copied_files'].append(destination)
        return True
