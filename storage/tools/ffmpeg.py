def get_ffprobe_info(filename):
    import tempfile
    import json
    from subprocess import Popen

    cmd = ("ffprobe", "-hide_banner", "-v", "quiet", "-print_format", "json",
           "-show_error", "-show_format", "-show_streams", filename)

    with tempfile.TemporaryFile("w+b") as f:
        # Use file to avoid PIPE's deadlock
        p = Popen(cmd, stdout=f)
        p.wait()

        f.seek(0)

        # for some reason ujson gets a segmentation error here, so use standard JSON library
        # result is 1-item list with a dict
        result = json.load(f)

        if result.get('error'):
            raise ValueError(f"ffprobe error code={result['error']['code']}: {result['error']['string']}")

        return result


def get_screenshot(filename, seconds_offset, hide_log=False, target=None):
    import os
    import tempfile
    from subprocess import Popen

    target = target or tempfile.TemporaryFile("w+b")

    cmd = ("ffmpeg", "-hide_banner", "-ss", seconds_offset, "-i", filename, "-frames:v", 1, "-q:v", 1, "-c:v", "mjpeg",
           "-f", "image2", "-")
    cmd = (str(c) for c in cmd)

    with open(os.devnull,"wb") as stderr:
        p = Popen(cmd, stdout=target, stderr=stderr if hide_log else None)
        p.wait()

    target.seek(0)

    assert not p.returncode

    return target