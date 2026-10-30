"""runner — logs in the disposable root and executes the activity script.

Static confine step for the F3 probe: PYTHONPATH is pinned to the root's own
``pylib`` and the root is handed over as argv[1]. This does NOT confine dynamic
filesystem access; the probe measures exactly where that static step stops.
"""
import os
import runpy
import sys


def main():
    root, script = sys.argv[1], sys.argv[2]
    os.chdir(root)                      # the activity's own working directory
    sys.path[:] = [os.path.join(root, "pylib")]
    runpy.run_path(script, run_name="__main__")


if __name__ == "__main__":
    main()
