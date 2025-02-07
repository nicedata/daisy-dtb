import os


from book.daisybook import DaisyBook
from navigators.toc_navigator import TocNavigator
from sources.folder_source import FolderDtbSource

SAMPLE_DTB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "../samples/valentin_hauy")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


folder_source = FolderDtbSource(SAMPLE_DTB_PROJECT_PATH)
web_source = FolderDtbSource(SAMPLE_DTB_PROJECT_URL)

folder_book = DaisyBook(folder_source)
web_book = DaisyBook(web_source)

folder_navigator = TocNavigator(folder_book._toc_entries, folder_book.navigation_depth)
web_navigator = TocNavigator(web_book._toc_entries, web_book.navigation_depth)
