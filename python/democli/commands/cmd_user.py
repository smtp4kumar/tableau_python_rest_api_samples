import click
from democli.cli import pass_context
from democli.utils.click_util import common_options
from democli.utils.log_util import create_logger

logger = create_logger(__name__)

# common options for sub commands
_common_options = [
    click.option(
        '-s', '--server', required=True, help='The specified server address'
    ),
    click.option(
        '-u', '--username', required=True, help='The username(not ID) of the user to sign in as'
    ),
    click.option(
        '-p', '--password', required=True, help='The password of the user to sign in as'
    )
]


@click.group('workbook', short_help='Root command to manage user and permission')
@pass_context
def cli(ctx):
    """Root command to manage user and permission"""
    pass


@cli.command('update_permission', short_help='Update user permission')
@common_options(_common_options)
@pass_context
def update_permission(ctx, server, username, password):
    """Update user permission"""
    # TODO


@cli.command('audit_permission', short_help='Audit user permission')
@common_options(_common_options)
@pass_context
def audit_permission(ctx, server, username, password):
    """Audit user permission"""
    # TODO


@cli.command('user_by_group', short_help='Fetch user by group')
@common_options(_common_options)
@pass_context
def user_by_group(ctx, server, username, password):
    """Fetch user by group"""
    # TODO
