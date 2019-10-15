from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import os

from phyloGenie_backend.settings import MEDIA_ROOT


class DriveConnector:
    def __init__(self):
        g_login = GoogleAuth()
        g_login.LocalWebserverAuth()
        self.drive = GoogleDrive(g_login)

    def export_to_google_drive(self, tree):
        file_path = os.path.join(MEDIA_ROOT, 'trees', str(tree))
        tree_newick = open(file_path, 'r')
        # tree_file = tree.open(mode='rb')

        file_drive = self.drive.CreateFile({'title': os.path.basename(str(tree))})
        file_drive.SetContentString(tree_newick.read())
        file_drive.Upload()
