import os
import sys
import click

# Providing ability to pass the value of command line option via environment variable
# Example - environment variable should be set as export DEMO_API_VERBOSE='true'
# Overall, value can be passed by respective command line or by environment variable or by config file.
# Fall-back order: command line -> environment variable -> from config file config.py
CONTEXT_SETTINGS = dict(auto_envvar_prefix='DEMO_API')


# Context object which get passed downstream
class Context(object):
    def __init__(self):
        self.verbose = False
        self.home = os.getcwd()

    def log(self, msg, *args):
        """Logs a message to stderr."""
        if args:
            msg %= args
        click.secho(msg + '\n', fg='green', file=sys.stderr)

    def vlog(self, msg, *args):
        """Logs a message to stderr only if verbose is enabled."""
        if self.verbose:
            self.log(msg, *args)


pass_context = click.make_pass_decorator(Context, ensure=True)
cmd_folder = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'commands')
)


# Main class to instantiate
class DemoCLI(click.MultiCommand):
    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(cmd_folder):
            if filename.endswith('.py') and filename.startswith('cmd_'):
                rv.append(filename[4:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info.major == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__(
                'democli.commands.cmd_' + name, None, None, ['cli']
            )
        except ImportError:
            return
        return mod.cli


@click.command(cls=DemoCLI, context_settings=CONTEXT_SETTINGS)
@click.option(
    '--home',
    type=click.Path(exists=True, file_okay=False, resolve_path=True),
    help='Changes the folder to operate on.'
)
@click.option(
    '-v', '--verbose',
    is_flag=True, help='Enables verbose mode.'
)
@pass_context
def cli(ctx, verbose, home):
    """Demo command line interface."""
    ctx.verbose = verbose
    if home is not None:
        ctx.home = home

