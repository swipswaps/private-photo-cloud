def get_exiftool_info(filename, numeric_values=False):
    import os
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
