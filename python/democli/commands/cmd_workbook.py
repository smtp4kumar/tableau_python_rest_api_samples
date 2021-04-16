import click
from democli.cli import pass_context
from democli.utils.click_util import common_options
from democli.utils.log_util import create_logger
from democli.auth.session_mgr import SessionMgr
from democli.workbook.workbook_mgr import WorkbookMgr

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


@click.group('workbook', short_help='Root command to manage workbook')
@pass_context
def cli(ctx):
    """Root command to manage workbook"""
    pass


@cli.command('move_to_project', short_help='Move workbook to destination project')
@common_options(_common_options)
@click.option(
    '-w', '--workbook_name', required=True, help='The name of workbook to move'
)
@click.option(
    '-d', '--dest_project', required=True, help='The destination project'
)
@pass_context
def move_to_project(ctx, server, username, password, workbook_name, dest_project):
    """Move workbook to destination project"""

    logger.info("\n*Moving '{0}' workbook to '{1}' project as {2}*".format(workbook_name, dest_project, username))

    ##### STEP 1: Sign in #####
    logger.info("\n1. Signing in as " + username)
    session_mgr = SessionMgr(server, username, password)
    auth_token, site_id, user_id = session_mgr.sign_in()

    ##### STEP 2: Find new project id #####
    logger.info("\n2. Finding project id of '{0}'".format(dest_project))
    workbook_mgr = WorkbookMgr(server, auth_token, site_id)
    dest_project_id = workbook_mgr.get_project_id(dest_project)

    ##### STEP 3: Find workbook id #####
    logger.info("\n3. Finding workbook id of '{0}'".format(workbook_name))
    source_project_id, workbook_id = workbook_mgr.get_workbook_id(user_id, workbook_name)

    # Check if the workbook is already in the desired project
    if source_project_id == dest_project_id:
        error = "Workbook already in destination project"
        raise UserDefinedFieldError(error)

    ##### STEP 4: Move workbook #####
    logger.info("\n4. Moving workbook to '{0}'".format(dest_project))
    workbook_mgr.move_workbook(workbook_id, dest_project_id)

    ##### STEP 5: Sign out #####
    logger.info("\n5. Signing out and invalidating the authentication token")
    session_mgr.sign_out(auth_token)


@cli.command('move_to_server', short_help='Move workbook to destination server')
@common_options(_common_options)
@click.option(
    '-w', '--workbook_name', required=True, help='The name of workbook to move'
)
@click.option(
    '--dest_server', required=True, help='The destination server'
)
@click.option(
    '--dest_username', required=True, help='The destination username'
)
@click.option(
    '--dest_password', required=True, help='The destination user password'
)
@click.option(
    '--dest_site_id', required=True, help='The destination site id'
)
@pass_context
def move_to_server(ctx, server, username, password, workbook_name, dest_server, dest_username, dest_password):
    """Move workbook to destination server"""

    logger.info("\n*Moving '{0}' workbook to the 'default' project in {1}*".format(workbook_name, dest_server))

    ##### STEP 1: Sign in #####
    logger.info("\n1. Signing in to both sites to obtain authentication tokens")
    # Source server
    source_session_mgr = SessionMgr(server, username, password)
    source_auth_token, source_site_id, source_user_id = source_session_mgr.sign_in()

    # Destination server
    dest_session_mgr = SessionMgr(dest_server, dest_username, dest_password)
    dest_auth_token, dest_site_id, dest_user_id = dest_session_mgr.sign_in()

    ##### STEP 2: Find workbook id #####
    logger.info("\n2. Finding workbook id of '{0}'".format(workbook_name))
    source_workbook_mgr = WorkbookMgr(server, source_auth_token, source_site_id)
    workbook_id = source_workbook_mgr.get_workbook_id(source_user_id, workbook_name)

    ##### STEP 3: Find 'default' project id for destination server #####
    logger.info("\n3. Finding 'default' project id for {0}".format(dest_server))
    dest_workbook_mgr = WorkbookMgr(dest_server, dest_auth_token, dest_site_id)
    dest_project_id = dest_workbook_mgr.get_default_project_id()

    ##### STEP 4: Download workbook #####
    logger.info("\n4. Downloading the workbook to move")
    workbook_filename = source_workbook_mgr.download(workbook_id)

    ##### STEP 5: Publish to new site #####
    logger.info("\n5. Publishing workbook to {0}".format(dest_server))
    dest_workbook_mgr.publish_workbook(workbook_filename, dest_project_id)

    ##### STEP 6: Deleting workbook from the source site #####
    logger.info("\n6. Deleting workbook from the original site and temp file")
    source_workbook_mgr.delete_workbook(workbook_id, workbook_filename)

    ##### STEP 7: Sign out #####
    logger.info("\n7. Signing out and invalidating the authentication token")
    source_session_mgr.sign_out(source_auth_token)
    dest_session_mgr.sign_out(dest_auth_token)


@cli.command('move_to_site', short_help='Move workbook to destination site')
@common_options(_common_options)
@click.option(
    '-w', '--workbook_name', required=True, help='The name of workbook to move'
)
@click.option(
    '--dest_site', required=True, help='The destination site id'
)
@pass_context
def move_to_site(ctx, server, username, password, workbook_name, dest_site):
    """Move workbook to destination site"""

    logger.info("\n*Moving '{0}' workbook to the 'default' project in {1}*".format(workbook_name, dest_site))

    ##### STEP 1: Sign in #####
    logger.info("\n1. Signing in to both sites to obtain authentication tokens")
    # Default site
    source_session_mgr = SessionMgr(server, username, password)
    source_auth_token, source_site_id, source_user_id = source_session_mgr.sign_in()

    # Specified site
    dest_session_mgr = SessionMgr(server, username, password, site=dest_site)
    dest_auth_token, dest_site_id, dest_user_id = dest_session_mgr.sign_in()

    ##### STEP 2: Find workbook id #####
    logger.info("\n2. Finding workbook id of '{0}' from source site".format(workbook_name))
    source_workbook_mgr = WorkbookMgr(server, source_auth_token, source_site_id)
    workbook_id = source_workbook_mgr.get_workbook_id(source_user_id, workbook_name)

    ##### STEP 3: Find 'default' project id for destination site #####
    logger.info("\n3. Finding 'default' project id for destination site")
    dest_workbook_mgr = WorkbookMgr(server, source_auth_token, dest_site_id)
    dest_project_id = dest_workbook_mgr.get_default_project_id(server, dest_auth_token, dest_site_id)

    ##### STEP 4: Download workbook #####
    logger.info("\n4. Downloading the workbook to move from source site")
    workbook_filename, workbook_content = source_workbook_mgr.download(workbook_id)

    ##### STEP 5: Publish to new site #####
    logger.info("\n5. Publishing workbook to destination site")
    dest_workbook_mgr.publish_workbook(workbook_filename, workbook_content, dest_project_id)

    ##### STEP 6: Deleting workbook from the source site #####
    logger.info("\n6. Deleting workbook from the source site")
    source_workbook_mgr.delete_workbook(workbook_id)

    ##### STEP 7: Sign out #####
    logger.info("\n7. Signing out and invalidating the authentication token")
    source_session_mgr.sign_out(source_auth_token)
    dest_session_mgr.sign_out(dest_auth_token)
