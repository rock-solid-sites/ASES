#!/usr/bin/env python3
"""Build minimal fixture and run it on the explicit managed Docker socket."""
import hashlib
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture"
EVIDENCE = HERE / "evidence"
IMAGE = "ases-uid-custody:phase-i-20261110"
DOCKER_HOST = "unix:///var/run/docker.sock"
IMAGE_REF = "python@sha256:5e2bdb1b0d542d5039cffb8181c65930093949194a65c365dfb1b0fe13a4fa5b"
UNSET = ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH")


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def docker(argv, timeout=180, legacy_builder=False):
    env = dict(os.environ)
    for key in UNSET:
        env.pop(key, None)
    if legacy_builder:
        # Keep DOCKER_CONFIG and credential state untouched. Buildx's cache
        # default is read-only in this executor; the fixture needs no BuildKit.
        env["DOCKER_BUILDKIT"] = "0"
    command = ["docker", f"--host={DOCKER_HOST}", *argv]
    try:
        result = subprocess.run(command, cwd=HERE, env=env, text=True,
                                capture_output=True, timeout=timeout, check=False)
        code, stdout, stderr = result.returncode, result.stdout, result.stderr
        timed_out = False
    except subprocess.TimeoutExpired as error:
        code = 124
        stdout = error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
        timed_out = True
    return {"argv": command, "exit": code,
            "stdout": stdout, "stderr": stderr[-3000:], "timed_out": timed_out,
            "buildkit_disabled_for_legacy_local_build": legacy_builder}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("final"))
    args = parser.parse_args()
    out = args.out if args.out.is_absolute() else EVIDENCE / args.out
    out = out.resolve()
    if EVIDENCE.resolve() not in out.parents:
        raise ValueError("--out must be a new directory beneath evidence/")
    out.mkdir(parents=True, exist_ok=False)
    started_ns = time.time_ns()
    files = sorted(path for path in FIXTURE.rglob("*") if path.is_file())
    allowed = {".dockerignore", "Dockerfile", "driver.py", "owner_supervisor.py", "worker_agent.py"}
    unexpected = [str(path.relative_to(FIXTURE)) for path in files
                  if ("/" not in str(path.relative_to(FIXTURE))
                      and str(path.relative_to(FIXTURE)) not in allowed)
                  or ("/" in str(path.relative_to(FIXTURE))
                      and not (str(path.relative_to(FIXTURE)).startswith("src/")
                               and path.suffix == ".py"))]
    source_files = [path for path in files if str(path.relative_to(FIXTURE)).startswith("src/")]
    if unexpected or len(source_files) != 5:
        raise RuntimeError("build context is not the frozen minimal source set")
    context_hashes = {str(path.relative_to(HERE)): sha(path.read_bytes()) for path in files}
    context_hash = sha(json.dumps(context_hashes, sort_keys=True, separators=(",", ":")).encode())
    daemon = docker(["info", "--format", "{{.ServerVersion}}|{{.Driver}}|{{.SecurityOptions}}"])
    if daemon["exit"] != 0:
        raise RuntimeError("managed Docker health read failed: " + daemon["stderr"])
    pinned_image = docker(["image", "inspect", IMAGE_REF, "--format", "{{.Id}}"], timeout=30)
    if pinned_image["exit"] != 0:
        raise RuntimeError("pinned Python image is unavailable: " + pinned_image["stderr"])
    built = docker(["build", "--network=none", "--tag", IMAGE, str(FIXTURE)],
                   timeout=180, legacy_builder=True)
    if built["exit"] != 0:
        (out / "build-failure.json").write_text(json.dumps(built, indent=2) + "\n")
        raise RuntimeError("minimal fixture build failed; failure retained")
    image_id = docker(["image", "inspect", IMAGE, "--format", "{{.Id}}"], timeout=30)
    task_id = f"uidcustody-{os.getpid()}-{time.time_ns()}"
    container_name = "ases-" + task_id
    run = docker(["run", "--rm", "--name", container_name,
                  "--label", "org.ases.uid-task=" + task_id,
                  "--network=none", "--cpus=1", "--memory=512m",
                  "--pids-limit=32", "--cap-drop=ALL", "--cap-add=CHOWN",
                  "--cap-add=DAC_OVERRIDE", "--cap-add=SETUID", "--cap-add=SETGID",
                  "--security-opt=no-new-privileges", IMAGE], timeout=90)
    cleanup = None
    if run["exit"] != 0:
        inspection = docker(["container", "inspect", container_name,
                             "--format", '{{ index .Config.Labels "org.ases.uid-task" }}|{{.Id}}'], timeout=10)
        if inspection["exit"] == 0:
            observed_label, _, observed_id = inspection["stdout"].strip().partition("|")
            if observed_label == task_id and observed_id:
                cleanup = docker(["container", "rm", "--force", container_name], timeout=15)
            else:
                cleanup = {"exit": 1, "reason": "exact task label did not match; left container untouched"}
        else:
            cleanup = {"exit": 0, "reason": "no exact named container remains"}
        run["exact_container_cleanup"] = cleanup
        (out / "run-failure.json").write_text(json.dumps(run, indent=2) + "\n")
        raise RuntimeError("native UID custody run failed; failure retained")
    raw = json.loads(run["stdout"])
    raw.update({"outer": {"started_ns": started_ns, "ended_ns": time.time_ns(),
                           "docker_server": daemon["stdout"].strip(),
                           "pinned_base_ref": IMAGE_REF,
                           "pinned_base_id": pinned_image["stdout"].strip(),
                           "built_image_id": image_id["stdout"].strip(),
                           "build_context_sha256": context_hash,
                           "build_context_file_hashes": context_hashes,
                           "container_name": container_name, "container_label": task_id,
                           "build_argv": built["argv"],
                           "buildkit_disabled_for_legacy_local_build": built["buildkit_disabled_for_legacy_local_build"],
                           "run_argv": run["argv"],
                           "run_exit": run["exit"], "run_stderr": run["stderr"]}})
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"execution": raw.get("execution"), "cases": list(raw.get("cases", {})),
                      "image_id": raw["outer"]["built_image_id"]}, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except BaseException as error:
        print(type(error).__name__ + ": " + str(error), file=sys.stderr)
        raise
