def get_sha1_hex(filename):
    """Faster alternative for getting SHA1 hash of a file"""
    from subprocess import Popen, PIPE

    cmd = ("sha1sum", filename)

    p = Popen(cmd, stdout=PIPE, stderr=PIPE)

    out, err = p.communicate()

    assert not p.returncode
    assert not err

    # stdout = b'<hash>  <filename>\n'

    return out.split(b' ', 1)[0].decode('utf-8')
