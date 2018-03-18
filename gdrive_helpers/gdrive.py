import httplib2
import os

from apiclient.http import MediaIoBaseDownload
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage


# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/drive-python-quickstart.json
SCOPES = ['https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Drive API Python Quickstart'


def get_credentials(secret_file=CLIENT_SECRET_FILE):
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(secret_file, SCOPES)
        flow.user_agent = APPLICATION_NAME
        print('Storing credentials to ' + credential_path)
    return credentials


def extract_id_from_url(url):
    return url.split('/')[-1]


def is_folder(item):
    return item['mimeType'] == 'application/vnd.google-apps.folder'


def download_folder_contents(folder_id, dest_path, service, http, n=1000):
    results = service.files().list(pageSize=n,
                                   q="'{}' in parents"
                                   .format(folder_id)).execute()
    if 'nextPageToken' in results.keys():
        raise RuntimeError("You missed some files! Implement pagination https://developers.google.com/drive/v3/web/search-parameters")

    folder_contents = results['files']
    files = (i for i in folder_contents if not is_folder(i))
    folders = (i for i in folder_contents if is_folder(i))

    if not os.path.exists(dest_path):
        os.makedirs(dest_path)

    for item in files:
        print(item)
        full_path = os.path.join(dest_path, item['name'].replace('/', '_'))
        download_file(item['id'], full_path, service)

    for item in folders:
        full_path = os.path.join(dest_path, item['name'].replace('/', '_'))
        print("found folder {}".format(full_path))
        download_folder_contents(item['id'], full_path, service, http)


def download_file(file_id, dest_path, service, overwrite=False):
    if not overwrite:
        if os.path.exists(dest_path):
            return None
    request = service.files().get_media(fileId=file_id)
    with open(dest_path, "wb+") as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download {} {}%."
                  .format(dest_path, int(status.progress() * 100)))


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    url = 'https://drive.google.com/drive/u/1/folders/1wUxW6d9vxSYNFRVtT4ZdNcZxQX-u1jr0'
    folder_id = extract_id_from_url(url)
    dest_path = './'
    download_folder_contents(folder_id, dest_path, service, http)


if __name__ == '__main__':
    main()
