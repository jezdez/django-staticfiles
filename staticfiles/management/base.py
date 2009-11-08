import logging
from optparse import make_option
from django.core.exceptions import ImproperlyConfigured
from django.core.management.base import BaseCommand, CommandError

class CommandLogger(object):
    """
    A mix-in for management commands to handle output via a logger.
    
    It must be the first parent class given for commands, so that the
    ``handle()`` method gets overridden.
    
    """
    logger_parent = 'staticfiles'
    logger_name = ''
    logger_format = '%(message)s'
    logger_levels = {'0': logging.ERROR, '1': logging.INFO, '2': logging.DEBUG}

    def get_logger(self):
        parts = [self.logger_parent, self.logger_name]
        name = '.'.join([part for part in parts if part])
        return logging.getLogger(name)
    
    def handle(self, *args, **kwargs):
        verbosity = kwargs.get('verbosity', '1')
        logger = logging.getLogger(self.logger_parent or self.logger_name)
        logger.setLevel(self.logger_levels[verbosity])
        handler = logging.StreamHandler()
        formatter = logging.Formatter(self.logger_format)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        try:
            return super(CommandLogger, self).handle(*args, **kwargs)
        finally:
            logger.removeHandler(handler)


class BaseOptionalAppCommand(BaseCommand):
    args = '[appname appname ...]'
    option_list = BaseCommand.option_list + (
        make_option('-e', '--exclude', dest='exclude', action='append',
            default=[], help='App to exclude (use multiple --exclude to '
            'exclude multiple apps).'),
    )

    def handle(self, *app_labels, **options):
        from django.db import models
        # Get all the apps, checking for common errors.
        try:
            all_apps = models.get_apps()
        except (ImproperlyConfigured, ImportError), e:
            raise CommandError("%s. Are you sure your INSTALLED_APPS setting "
                               "is correct?" % e)
        # Build the app_list.
        app_list = []
        used = 0
        for app in all_apps:
            app_label = app.__name__.split('.')[-2]
            if not app_labels or app_label in app_labels:
                used += 1
                if app_label not in options['exclude']:
                    app_list.append(app)
        # Check that all app_labels were used.
        if app_labels and used != len(app_labels): 
            raise CommandError('Could not find the following app(s): %s' %
                               ', '.join(app_labels))
        # Handle all the apps (either via handle_app or excluded_app),
        # collating any output.
        output = []
        pre_output = self.pre_handle_apps(**options)
        if pre_output:
            output.append(pre_output)
        for app in all_apps:
            if app in app_list:
                handle_method = self.handle_app
            else:
                handle_method = self.excluded_app
            app_output = handle_method(app, **options)
            if app_output:
                output.append(app_output)
        post_output = self.post_handle_apps(**options)
        if post_output:
            output.append(post_output)
        return '\n'.join(output)

    def handle_app(self, app, **options):
        """
        Perform the command's actions for ``app``, which will be the
        Python module corresponding to an application name given on
        the command line.
        
        """
        raise NotImplementedError()

    def excluded_app(self, app, **options):
        """
        A hook for commands to parse apps which were excluded.
        
        """

    def pre_handle_apps(self, **options):
        """
        A hook for commands to do something before the applications are
        processed.
        
        """

    def post_handle_apps(self, **options):
        """
        A hook for commands to do something after all applications have been
        processed.
        
        """


class OptionalAppCommand(CommandLogger, BaseOptionalAppCommand):
    """
    A management command which optionally takes one or more installed
    application names as arguments, and does something with each of them.
    
    If no application names are provided, all the applications are used.
    
    The order in which applications are processed is determined by the order
    given in INSTALLED_APPS. This differs from Django's AppCommand (it uses the
    order the apps are given in the management command).

    Rather than implementing ``handle()``, subclasses must implement
    ``handle_app()``, which will be called once for each application.
    
    Subclasses can also optionally implement ``excluded_app()`` to run
    processes on apps which were excluded.
    
    """
