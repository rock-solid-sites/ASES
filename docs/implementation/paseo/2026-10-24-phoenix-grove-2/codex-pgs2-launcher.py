#!/usr/bin/python3
"""Load only Phoenix Grove subscription 2 credentials, then run pinned Codex."""
import os, pathlib, stat
path = pathlib.Path('/home/claude-code/.secrets/paseo-pgs2.key')
directory = path.parent.lstat()
if not stat.S_ISDIR(directory.st_mode) or directory.st_uid != os.getuid() or stat.S_IMODE(directory.st_mode) != 0o700:
    raise SystemExit('Unsafe subscription 2 credential directory permissions.')
fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
with os.fdopen(fd, 'rb') as stream:
    info = os.fstat(stream.fileno())
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600:
        raise SystemExit('Unsafe subscription 2 credential file permissions.')
    raw = stream.read(4097)
if len(raw) > 4096:
    raise SystemExit('Invalid subscription 2 credential file.')
try:
    key = raw.decode('ascii').rstrip('\n')
except UnicodeError:
    raise SystemExit('Invalid subscription 2 credential format.')
if not key or any(c.isspace() or ord(c) < 33 or ord(c) == 127 for c in key):
    raise SystemExit('Invalid subscription 2 credential format.')
os.umask(0o077)
os.environ['OPENAI_API_KEY'] = key
os.environ['OPENAI_BASE_URL'] = 'https://api.pgsgrove.com/v1'
os.environ['CODEX_HOME'] = '/home/claude-code/.paseo/codex-pgs2'
binary = '/home/claude-code/.codex/packages/standalone/releases/0.157.1-x86_64-unknown-linux-musl/bin/codex'
os.execv(binary, [binary, *os.sys.argv[1:]])
