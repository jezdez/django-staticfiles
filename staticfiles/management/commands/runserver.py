import os
import django
import sys
from optparse import make_option

from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler
from django.core.servers.basehttp import run, WSGIServerException
from django.core.management.base import BaseCommand, CommandError

from staticfiles.handlers import StaticFilesHandler

try:
    # Use upstream runserver command if existing
    from django.contrib.staticfiles.management.commands.runserver import Command as RunserverCommand

    class Command(RunserverCommand):
        """
        Subclass of the standard runserver command that overrides the
        staticfiles handler to use this app's finders.
        """
        def get_handler(self, *args, **options):
            """
            Returns the static files serving handler.
            """
            handler = WSGIHandler()
            use_static_handler = options.get('use_static_handler', True)
            insecure_serving = options.get('insecure_serving', False)
            if use_static_handler and (settings.DEBUG or insecure_serving):
                handler = StaticFilesHandler(handler)
            return handler

except ImportError:

    # No upstream staticfiles runserver found, create our own bare bones command
    class Command(BaseCommand):
        option_list = BaseCommand.option_list + (
            make_option('--noreload',
                action='store_false', dest='use_reloader', default=True,
                help='Tells Django to NOT use the auto-reloader.'),
            make_option('--nostatic',
                action="store_false", dest='use_static_handler', default=True,
                help='Tells Django to NOT automatically serve static files at STATIC_URL.'),
            make_option('--insecure',
                action="store_true", dest='insecure_serving', default=False,
                help='Allows serving static files even if DEBUG is False.'),
        )
        help = "Starts a lightweight Web server for development and also serves static files."
        args = '[optional port number, or ipaddr:port]'

        def get_handler(self, *args, **options):
            """
            Returns the static files serving handler.
            """
            handler = WSGIHandler()
            use_static_handler = options.get('use_static_handler', True)
            insecure_serving = options.get('insecure_serving', False)
            if use_static_handler and (settings.DEBUG or insecure_serving):
                handler = StaticFilesHandler(handler)
            return handler

        def handle(self, addrport='', *args, **options):
            if args:
                raise CommandError('Usage is runserver %s' % self.args)
            if not addrport:
                addr = ''
                port = '8000'
            else:
                try:
                    addr, port = addrport.split(':')
                except ValueError:
                    addr, port = '', addrport
            if not addr:
                addr = '127.0.0.1'

            if not port.isdigit():
                raise CommandError("%r is not a valid port number." % port)

            use_reloader = options.get('use_reloader', True)
            shutdown_message = options.get('shutdown_message', '')
            quit_command = (sys.platform == 'win32') and 'CTRL-BREAK' or 'CONTROL-C'

            def inner_run():
                from django.conf import settings
                from django.utils import translation
                print "Validating models..."
                self.validate(display_num_errors=True)
                print "\nDjango version %s, using settings %r" % (django.get_version(), settings.SETTINGS_MODULE)
                print "Development server is running at http://%s:%s/" % (addr, port)
                print "Quit the server with %s." % quit_command

                # django.core.management.base forces the locale to en-us. We should
                # set it up correctly for the first request (particularly important
                # in the "--noreload" case).
                translation.activate(settings.LANGUAGE_CODE)

                try:
                    handler = self.get_handler(*args, **options)
                    run(addr, int(port), handler)
                except WSGIServerException, e:
                    # Use helpful error messages instead of ugly tracebacks.
                    ERRORS = {
                        13: "You don't have permission to access that port.",
                        98: "That port is already in use.",
                        99: "That IP address can't be assigned-to.",
                    }
                    try:
                        error_text = ERRORS[e.args[0].args[0]]
                    except (AttributeError, KeyError):
                        error_text = str(e)
                    sys.stderr.write(self.style.ERROR("Error: %s" % error_text) + '\n')
                    # Need to use an OS exit because sys.exit doesn't work in a thread
                    os._exit(1)
                except KeyboardInterrupt:
                    if shutdown_message:
                        print shutdown_message
                    sys.exit(0)

            if use_reloader:
                from django.utils import autoreload
                autoreload.main(inner_run)
            else:
                inner_run()
