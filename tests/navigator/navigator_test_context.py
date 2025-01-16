import os

from dtbsource import FolderDtbResource
from develop import DaisyDtb, NccNavigator

SAMPLE_DTB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "../samples/valentin_hauy")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"

folder_source = FolderDtbResource(SAMPLE_DTB_PROJECT_PATH)
web_source = FolderDtbResource(SAMPLE_DTB_PROJECT_URL)

folder_book = DaisyDtb(folder_source)
web_book = DaisyDtb(web_source)

folder_navigator = NccNavigator(folder_book)
web_navigator = NccNavigator(web_book)
