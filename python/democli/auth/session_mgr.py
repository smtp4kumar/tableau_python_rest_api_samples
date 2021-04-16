import requests
from democli.utils.log_util import create_logger
from democli.utils.http_util import check_status
from democli.utils.common_util import encode_for_display
from democli.version import VERSION
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML

logger = create_logger(__name__)


# Class for managing login sessions
class SessionMgr:
    def __init__(self, ctx, server, username, password, site=""):
        """
        'server'   specified server address
        'name'     is the name (not ID) of the user to sign in as.
                   Note that most of the functions in this example require that the user
                   have server administrator permissions.
        'password' is the password for the user.
        'site'     is the ID (as a string) of the site on the server to sign in to. The
                   default is "", which signs in to the default site.
        """
        self.ctx = ctx
        self.server = server
        self.username = username
        self.password = password
        self.site = site

    def sign_in(self):
        """
        Signs in to the server specified with the given credentials

        Returns the authentication token and the site ID.
        """
        url = self.server + "/api/{0}/auth/signin".format(VERSION)

        # Builds the request
        xml_request = ET.Element('tsRequest')
        credentials_element = ET.SubElement(xml_request, 'credentials', name=self.username, password=self.password)
        ET.SubElement(credentials_element, 'site', contentUrl=self.site)
        xml_request = ET.tostring(xml_request)

        # Make the request to server
        server_response = requests.post(url, data=xml_request)
        check_status(server_response, 200)

        # ASCII encode server response to enable displaying to console
        server_response = encode_for_display(server_response.text)

        # Reads and parses the response
        parsed_response = ET.fromstring(server_response)

        # Gets the auth token and site ID
        token = parsed_response.find('t:credentials', namespaces=xmlns).get('token')
        site_id = parsed_response.find('.//t:site', namespaces=xmlns).get('id')
        user_id = parsed_response.find('.//t:user', namespaces=xmlns).get('id')
        return token, site_id, user_id

    def sign_out(self, auth_token):
        """
        Destroys the active session and invalidates authentication token.

        'auth_token'    authentication token that grants user access to API calls
        """

        url = self.server + "/api/{0}/auth/signout".format(VERSION)
        server_response = requests.post(url, headers={'x-tableau-auth': auth_token})
        check_status(server_response, 204)
        return
