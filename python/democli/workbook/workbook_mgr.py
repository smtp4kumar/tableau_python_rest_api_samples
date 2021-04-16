import requests, os
from democli.utils.log_util import create_logger
from democli.utils.http_util import check_status, make_multipart
from democli.utils.common_util import encode_for_display
from democli.version import VERSION
import xml.etree.ElementTree as ET  # Contains methods used to build and parse XML

logger = create_logger(__name__)

# The maximum size of a file that can be published in a single request is 64MB
FILESIZE_LIMIT = 1024 * 1024 * 64  # 64MB

# For when a workbook is over 64MB, break it into 5MB(standard chunk size) chunks
CHUNK_SIZE = 1024 * 1024 * 5  # 5MB


# Class for managing workbook
class WorkbookMgr:
    def __init__(self, ctx, server, auth_token, site_id):
        """
        'server'        specified server address
        'auth_token'    authentication token that grants user access to API calls
        'site_id'       ID of the site that the user is signed into
        """
        self.ctx = ctx
        self.server = server
        self.auth_token = auth_token
        self.site_id = site_id

    def get_workbook_id(self, user_id, workbook_name):
        """
        Gets the id of the desired workbook to relocate.

        'user_id'       ID of user with access to workbook
        'workbook_name' name of workbook to get ID of
        Returns the workbook id and the project id that contains the workbook.
        """
        url = self.server + "/api/{0}/sites/{1}/users/{2}/workbooks".format(VERSION, self.site_id, user_id)
        server_response = requests.get(url, headers={'x-tableau-auth': self.auth_token})
        check_status(server_response, 200)
        xml_response = ET.fromstring(encode_for_display(server_response.text))

        workbooks = xml_response.findall('.//t:workbook', namespaces=xmlns)
        for workbook in workbooks:
            if workbook.get('name') == workbook_name:
                source_project_id = workbook.find('.//t:project', namespaces=xmlns).get('id')
                return source_project_id, workbook.get('id')
        error = "Workbook named '{0}' not found.".format(workbook_name)
        raise LookupError(error)

    def move_workbook(self, workbook_id, project_id):
        """
        Moves the specified workbook to another project.

        'workbook_id'   ID of the workbook to move
        'project_id'    ID of the project to move workbook into
        """
        url = self.server + "/api/{0}/sites/{1}/workbooks/{2}".format(VERSION, self.site_id, workbook_id)
        # Build the request to move workbook
        xml_request = ET.Element('tsRequest')
        workbook_element = ET.SubElement(xml_request, 'workbook')
        ET.SubElement(workbook_element, 'project', id=project_id)
        xml_request = ET.tostring(xml_request)

        server_response = requests.put(url, data=xml_request, headers={'x-tableau-auth': self.auth_token})
        check_status(server_response, 200)

    def get_default_project_id(self):
        """
        Returns the project ID for the 'default' project on the Tableau server.

        """
        page_num, page_size = 1, 100  # Default paginating values

        # Builds the request
        url = self.server + "/api/{0}/sites/{1}/projects".format(VERSION, self.site_id)
        paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page_num)
        server_response = requests.get(paged_url, headers={'x-tableau-auth': self.auth_token})
        check_status(server_response, 200)
        xml_response = ET.fromstring(encode_for_display(server_response.text))

        # Used to determine if more requests are required to find all projects on server
        total_projects = int(xml_response.find('t:pagination', namespaces=xmlns).get('totalAvailable'))
        max_page = int(math.ceil(total_projects / page_size))

        projects = xml_response.findall('.//t:project', namespaces=xmlns)

        # Continue querying if more projects exist on the server
        for page in range(2, max_page + 1):
            paged_url = url + "?pageSize={0}&pageNumber={1}".format(page_size, page)
            server_response = requests.get(paged_url, headers={'x-tableau-auth': self.auth_token})
            check_status(server_response, 200)
            xml_response = ET.fromstring(encode_for_display(server_response.text))
            projects.extend(xml_response.findall('.//t:project', namespaces=xmlns))

        # Look through all projects to find the 'default' one
        for project in projects:
            if project.get('name') == 'default' or project.get('name') == 'Default':
                return project.get('id')
        raise LookupError("Project named 'default' was not found on server")

    def start_upload_session(self):
        """
        Creates a POST request that initiates a file upload session.

        Returns a session ID that is used by subsequent functions to identify the upload session.
        """
        url = self.server + "/api/{0}/sites/{1}/fileUploads".format(VERSION, self.site_id)
        server_response = requests.post(url, headers={'x-tableau-auth': self.auth_token})
        check_status(server_response, 201)
        xml_response = ET.fromstring(encode_for_display(server_response.text))
        return xml_response.find('t:fileUpload', namespaces=xmlns).get('uploadSessionId')

    def download(self, workbook_id):
        """
        Downloads the desired workbook from the server (temp-file).

        'workbook_id'   ID of the workbook to download
        Returns the filename of the workbook downloaded.
        """
        print("\tDownloading workbook to a temp file")
        url = self.server + "/api/{0}/sites/{1}/workbooks/{2}/content".format(VERSION, self.site_id, workbook_id)
        server_response = requests.get(url, headers={'x-tableau-auth': self.auth_token})
        check_status(server_response, 200)

        # Header format: Content-Disposition: name="tableau_workbook"; filename="workbook-filename"
        filename = re.findall(r'filename="(.*)"', server_response.headers['Content-Disposition'])[0]
        with open(filename, 'wb') as f:
            f.write(server_response.content)
        return filename

    def publish_workbook(self, workbook_filename, dest_project_id):
        """
        Publishes the workbook to the desired project.

        'workbook_filename' filename of workbook to publish
        'dest_project_id'   ID of peoject to publish to
        """
        workbook_name, file_extension = workbook_filename.split('.', 1)
        workbook_size = os.path.getsize(workbook_filename)
        chunked = workbook_size >= FILESIZE_LIMIT

        # Build a general request for publishing
        xml_request = ET.Element('tsRequest')
        workbook_element = ET.SubElement(xml_request, 'workbook', name=workbook_name)
        ET.SubElement(workbook_element, 'project', id=dest_project_id)
        xml_request = ET.tostring(xml_request)

        if chunked:
            print("\tPublishing '{0}' in {1}MB chunks (workbook over 64MB):".format(workbook_name, CHUNK_SIZE / 1024000))
            # Initiates an upload session
            upload_id = self.start_upload_session()

            # URL for PUT request to append chunks for publishing
            put_url = self.server + "/api/{0}/sites/{1}/fileUploads/{2}".format(VERSION, self.site_id, upload_id)

            # Reads and uploads chunks of the workbook
            with open(workbook_filename, 'rb') as f:
                while True:
                    data = f.read(CHUNK_SIZE)
                    if not data:
                        break
                    payload, content_type = make_multipart({'request_payload': ('', '', 'text/xml'),
                                                            'tableau_file': ('file', data, 'application/octet-stream')})
                    print("\tPublishing a chunk...")
                    server_response = requests.put(put_url, data=payload,
                                                   headers={'x-tableau-auth': self.auth_token, "content-type": content_type})
                    check_status(server_response, 200)

            # Finish building request for chunking method
            payload, content_type = make_multipart({'request_payload': ('', xml_request, 'text/xml')})

            publish_url = self.server + "/api/{0}/sites/{1}/workbooks".format(VERSION, self.site_id)
            publish_url += "?uploadSessionId={0}".format(upload_id)
            publish_url += "&workbookType={0}&overwrite=true".format(file_extension)
        else:
            print("\tPublishing '{0}' using the all-in-one method (workbook under 64MB)".format(workbook_name))

            # Read the contents of the file to publish
            with open(workbook_filename, 'rb') as f:
                workbook_bytes = f.read()

            # Finish building request for all-in-one method
            parts = {'request_payload': ('', xml_request, 'text/xml'),
                     'tableau_workbook': (workbook_filename, workbook_bytes, 'application/octet-stream')}
            payload, content_type = make_multipart(parts)

            publish_url = self.server + "/api/{0}/sites/{1}/workbooks".format(VERSION, self.site_id)
            publish_url += "?workbookType={0}&overwrite=true".format(file_extension)

        # Make the request to publish and check status code
        print("\tUploading...")
        server_response = requests.post(publish_url, data=payload,
                                        headers={'x-tableau-auth': self.auth_token, 'content-type': content_type})
        check_status(server_response, 201)

    def delete_workbook(self, workbook_id, workbook_filename):
        """
        Deletes the temp workbook file, and workbook from the source project.

        'workbook_id'       ID of workbook to delete
        'workbook_filename' filename of temp workbook file to delete
        """
        # Builds the request to delete workbook from the source project on server
        url = self.server + "/api/{0}/sites/{1}/workbooks/{2}".format(VERSION, self.site_id, workbook_id)
        server_response = requests.delete(url, headers={'x-tableau-auth': self.auth_token})
        check_status(server_response, 204)

        # Remove the temp file created for the download
        os.remove(workbook_filename)
