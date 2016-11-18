import logging
import re

from PIL import Image

logger = logging.getLogger(__name__)


def get_exiftool_info(filename, numeric_values=False):
    import tempfile
    import json
    from subprocess import Popen

    if numeric_values:
        cmd = ("exiftool", '-groupNames', '-n', '-json', '-sort', filename)
    else:
        cmd = ("exiftool", '-groupNames', '-json', '-sort', filename)

    with tempfile.TemporaryFile("w+b") as f:
        # Use file to avoid PIPE's deadlock
        p = Popen(cmd, stdout=f)
        p.wait()

        f.seek(0)

        if p.returncode:
            raise RuntimeError(f'Command {" ".join(cmd)} exit with code {p.returncode}')

        # for some reason ujson gets a segmentation error here, so use standard JSON library
        # result is 1-item list with a dict
        return json.load(f)[0]


def extract_embed_resource(filename, resource, target=None, hide_log=False):
    """
    Sources:
        exiftool -b -ThumbnailImage image.jpg > thumbnail.jpg
             Save thumbnail image from "image.jpg" to a file called
             "thumbnail.jpg".

        exiftool -b -JpgFromRaw -w _JFR.JPG -ext NEF -r .
             Recursively extract JPG image from all Nikon NEF files in the
             current directory, adding "_JFR.JPG" for the name of the output JPG
             files.

        exiftool -a -b -W %d%f_%t%-c.%s -preview:all dir
             Extract all types of preview images (ThumbnailImage, PreviewImage,
             JpgFromRaw, etc.) from files in directory "dir", adding the tag
             name to the output preview image file names.
    """
    import os
    import tempfile
    from subprocess import Popen

    target = target or tempfile.TemporaryFile("w+b")

    cmd = ("exiftool", "-b", f'-{resource}', filename)

    with open(os.devnull,"wb") as stderr:
        p = Popen(cmd, stdout=target, stderr=stderr if hide_log else None)
        p.wait()

    target.seek(0)

    assert not p.returncode

    return target


RE_BINARY_VALUE = re.compile(r'^[(]Binary data (\d+) bytes, use -b option to extract[)]$')


def list_embed_resources(metadata):
    data = ((k, RE_BINARY_VALUE.search(v)) for k, v in metadata.items() if isinstance(v, str))
    return {k.rsplit(':', 1)[1]: int(m.group(1), 10) for k, m in data if m}


def check_if_image(fp):
    try:
        # Do not use Image context manager since it would close fp
        Image.open(fp)
        return True
    except OSError:
        return False
    finally:
        fp.seek(0)


def extract_any_embed_image(metadata, filename, target=None, hide_log=False, biggest=False):
    # Get binary resources
    binary_resources = list_embed_resources(metadata)

    # Sort by size
    binary_resources = sorted(binary_resources.items(), key=lambda x: x[1], reverse=biggest)

    logger.debug(f'Found binary resources: {binary_resources}')

    for resource, size in binary_resources:
        # We could check if name contains "data", e.g. "OriginalDecisionData" but we could simply check for an image
        result = extract_embed_resource(filename=filename, resource=resource, target=target, hide_log=hide_log)

        if not check_if_image(result):
            logger.info(f'Resource {resource} is not a image')
            continue

        logger.info(f'Used resource {resource} as an image')
        return result

    raise ValueError(f'Found no image in resources: {binary_resources}')
