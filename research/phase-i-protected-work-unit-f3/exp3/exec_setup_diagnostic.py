import os, subprocess, sys
import mediator_revocation as probe

read_fd, write_fd = os.pipe()

def preexec():
    try:
        probe.confine_before_exec()
        os.write(write_fd, b"LANDLOCK_SETUP_OK\n")
    except BaseException as exc:
        detail = "LANDLOCK_SETUP_ERROR type=%s errno=%r detail=%r\n" % (
            type(exc).__name__, getattr(exc, "errno", None), str(exc))
        os.write(write_fd, detail.encode())
        raise
    finally:
        os.close(write_fd)

try:
    p = subprocess.Popen([sys.executable, "-S", "-c", "print('exec-ready')"],
                         preexec_fn=preexec, pass_fds=(write_fd,),
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                         text=True, close_fds=True)
    os.close(write_fd)
    detail = os.read(read_fd, 4096).decode("utf-8", "replace").strip()
    out, _ = p.communicate(timeout=4)
    print("status_pipe=%r exit=%d stdout=%r" % (detail, p.returncode, out.strip()))
except BaseException as exc:
    try:
        os.close(write_fd)
    except OSError:
        pass
    detail = os.read(read_fd, 4096).decode("utf-8", "replace").strip()
    print("status_pipe=%r parent_error=%s:%s" % (detail, type(exc).__name__, exc))
finally:
    os.close(read_fd)