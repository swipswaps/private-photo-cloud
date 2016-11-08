def get_ffprobe_info(filename):
    import os
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

        if p.returncode:
            raise RuntimeError(f'Command {" ".join(cmd)} exit with code {p.returncode}')

        # for some reason ujson gets a segmentation error here, so use standard JSON library
        # result is 1-item list with a dict
        return json.load(f)
