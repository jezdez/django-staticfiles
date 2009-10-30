import fnmatch
import os
import shutil
import sys
from optparse import make_option

from django.core.files.storage import FileSystemStorage
from django.core.management.base import CommandError

from staticfiles.management.base import OptionalAppCommand
from staticfiles.settings import DIRS, EXCLUDED_APPS, MEDIA_DIRNAMES, \
    STORAGE, PREPEND_LABEL_APPS
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
    help = ("Collect media files from apps and other locations in a single "
            "media directory.")

    def handle(self, ignore_patterns, *app_labels, **options):
        options['skipped_files'] = []
        options['copied_files'] = []
        storage = utils.dynamic_import(STORAGE)()
        options['destination_storage'] = storage
        try:
            destination_paths = self.get_files(storage, ignore_patterns)
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
        for name, dir in DIRS:
            self.handle_dir(dir=dir, ignore_patterns=ignore_patterns,
                            destination_prepend=name, **options)
        return super(Command, self).handle(ignore_patterns=ignore_patterns,
                                           *app_labels, **options)

    def handle_dir(self, dir, ignore_patterns, destination_prepend, **options):
        """
        Copy all files from a directory.
        
        """
        source_storage = FileSystemStorage(location=dir)
        for source in self.get_files(source_storage, ignore_patterns):
            destination = self.destination_prepend(source,
                                                   destination_prepend)
            self.copy_file(source, destination, source_storage, **options)

    def post_handle(self, copied_files, **options):
        logger = self.get_logger()
        count = len(copied_files)
        logger.info("%s static file%s built." % (count,
                                                 count != 1 and 's' or ''))

    def handle_app(self, app, **options):
        """
        Copy all static media files from an application.
        
        """
        self.get_files_for_app(app, copy=True, **options)

    def excluded_app(self, app, skipped_files, **options):
        """
        Gather all the static media files for excluded apps.
        
        This is so a warning can be issued for later copied files which would
        normally be copied by excluded apps.
        
        """
        all_files = self.get_files_for_app(app, **options)
        skipped_files.extend(all_files)

    def get_files_for_app(self, app, ignore_patterns, destination_storage,
                          dry_run, copy=False, **options):
        """
        Return a list of tuples containing the relative destination paths for
        all files that should be copied for an app.
        
        If ``copy`` argument is True, the files are actually copied.
        
        """
        logger = self.get_logger()
        if app in EXCLUDED_APPS:
            return []
        bits = app.__name__.split('.')[:-1]
        app_name = bits[-1]
        if '.'.join(bits) in PREPEND_LABEL_APPS:
            destination_prepend = app_name
        else:
            destination_prepend = None
        app_root = os.path.dirname(app.__file__)
        destination_paths = []
        for media_dirname in MEDIA_DIRNAMES:
            location = os.path.join(app_root, media_dirname)
            if not os.path.isdir(location):
                continue
            logger.debug('Media location %r found for %r app.' %
                         (media_dirname, app_name))
            source_storage = FileSystemStorage(location=location)
            for source in self.get_files(source_storage, ignore_patterns):
                if destination_prepend:
                    destination = '/'.join([destination_prepend, source])
                else:
                    destination = source
                if copy:
                    self.copy_file(source, destination, source_storage,
                                   destination_storage, dry_run, **options)
                destination_paths.append(destination)
        return destination_paths

    def get_files(self, storage, ignore_patterns, location=''):
        """
        Recursively walk the storage directories gathering a complete list of
        files that should be copied, returning this list.
        
        """
        directories, files = storage.listdir(location)
        static_files = [location and '/'.join([location, fn]) or fn
                        for fn in files
                        if not self.is_ignored(fn, ignore_patterns)]
        for dir in directories:
            if self.is_ignored(dir, ignore_patterns):
                continue
            if location:
                dir = '/'.join([location, dir])
            static_files.extend(self.get_files(storage, ignore_patterns, dir))
        return static_files

    def is_ignored(self, path, ignore_patterns):
        """
        Return True or False depending on whether the ``path`` should be
        ignored (if it matches any pattern in ``ignore_patterns``).
        
        """
        for pattern in ignore_patterns:
            if fnmatch.fnmatchcase(path, pattern):
                return True
        return False

    def copy_file(self, source, destination, source_storage,
                  destination_storage, dry_run, **options):
        """
        Attempt to copy (or symlink) `source` to `destination`, returning True
        if successful.
        """
        logger = self.get_logger()
        if destination in options['copied_files']:
            logger.warning("Skipping duplicate file: %s" % destination)
            return False
        if destination in options['copied_files']:
            logger.warning("Copying file that would normally be provided by "
                           "an excluded application: %s" % destination)
            return False
        source_path = source_storage.path(source)
        if destination in options['destination_paths']:
            if dry_run:
                logger.info("Pretending to delete %r" % destination)
            else:
                logger.debug("Deleting %r" % destination)
                destination_storage.delete(destination)
        if options['link']:
            destination_path = destination_storage.path(destination)
            if dry_run:
                logger.info("Pretending to symlink %r to %r" % (source_path,
                                                            destination_path))
            else:
                logger.debug("Symlinking %r to %r" % (source_path,
                                                      destination_path))
                os.symlink(source_path, destination_path)
        if dry_run:
            logger.info("Pretending to copy %r to %r" % (source_path,
                                                         destination))
        else:
            logger.debug("Copying %r to %r" % (source_path, destination))
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
