import os
from typing import List

from loguru import logger

from daisy import Dtb
from dtbsource import DtbResource, FolderDtbResource

SAMPLE_DTB_PROJECT_PATH = os.path.join(os.path.dirname(__file__), "../tests/samples/valentin_hauy")
SAMPLE_DTB_PROJECT_URL = "https://www.daisyplayer.ch/aba-data/GuidePratique"


def test(source: DtbResource):
    logger.info(f"Working on {source.resource_base}")
    logger.info(f"Source class is {source.__class__.__name__}")
    logger.info(f"Source {source.resource_base} is OK")

    dtb = Dtb(source)
    logger.info(f"The DTB was correctly loaded: {dtb.is_valid}")
    logger.info(f"Metadata count: {len(dtb.metadata)}")
    logger.info(f"Ncc entries count: {len(dtb.entries)}")
    logger.info(f"Smil count: {len(dtb.smils)}")

    for smil in dtb.smils:
        logger.info(f"Loading smil {smil.reference.resource} ...")
        smil.load()
        logger.info(f"Smil {smil.reference.resource} - Loaded {smil.is_loaded}")

    logger.info(f"Finished working on {source.resource_base}\n")


def main():
    """Perform tests !"""
    paths = [SAMPLE_DTB_PROJECT_PATH, SAMPLE_DTB_PROJECT_URL]
    paths = [SAMPLE_DTB_PROJECT_PATH]
    sources: List[DtbResource] = []

    for path in paths:
        try:
            if path.startswith("http"):
                sources.append(FolderDtbResource(path))
            else:
                sources.append(FolderDtbResource(path))
        except FileNotFoundError:
            logger.critical(f"Source {path} not found.")
            return

    for source in sources:
        test(source)


if __name__ == "__main__":
    main()
