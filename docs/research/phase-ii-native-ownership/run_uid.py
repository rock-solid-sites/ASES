#!/usr/bin/env python3
"""Run the actual native ownership path inside the pinned #27 UID boundary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE_TAG = "ases-uid-custody:phase-i-20261110"
BASE_ID = "sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335"
UNSET = ("DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH")


def docker(arguments, timeout=180, build=False):
    env = dict(os.environ)
    for key in UNSET: env.pop(key, None)
    if build: env["DOCKER_BUILDKIT"] = "0"  # #27's supported local builder; config untouched.
    argv = ["docker", "--host=unix:///var/run/docker.sock", *arguments]
    try:
        result = subprocess.run(argv, env=env, capture_output=True, text=True, timeout=timeout)
        return dict(argv=argv, exit=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        return dict(argv=argv, exit=124, stdout=(error.stdout or b"").decode(errors="replace")
                    if isinstance(error.stdout, bytes) else error.stdout or "",
                    stderr=(error.stderr or b"").decode(errors="replace")
                    if isinstance(error.stderr, bytes) else error.stderr or "", timed_out=True)


def sha(raw): return hashlib.sha256(raw).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    task = f"ases4-uid-{os.getpid()}-{time.time_ns()}"
    tag = "ases4-native-ownership:" + task
    facts = dict(task=task, started_ns=time.time_ns(), base_ref=BASE_TAG, base_id=BASE_ID)
    base = docker(["image", "inspect", BASE_TAG, "--format", "{{.Id}}"])
    facts["base_inspection"] = base
    if base["exit"] or base["stdout"].strip() != BASE_ID:
        (out / "failure.json").write_text(json.dumps(facts, indent=2) + "\n")
        raise RuntimeError("pinned #27 local image unavailable or changed; no replacement image inferred")
    files = set()
    runtime = {
        "phase-ii-native-ownership": ("native_owner.py", "owner_cli.py", "native_sink.py", "unix_transport.py", "probe.py"),
        "phase-i-continuation-stack": ("continuation_sink.py",),
        "phase-i-composed-effects": ("composed_sink.py",),
        "phase-i-effect-admission": ("admission.py", "admission_sink.py"),
        "phase-i-effect-retry": ("candidate.py",),
        "phase-i-cold-activation": ("cold_sink.py",),
        "phase-i-f1-recovery-repair": ("repaired_service.py", "probe.py"),
        "phase-i-sol-integration": ("native.py",),
    }
    for directory, names in runtime.items():
        files.update(REPO / "docs/research" / directory / name for name in names)
    for name in ("f1", "l5", "l6", "receipt"):
        files.update((REPO / "docs/research/phase-i-sol-integration/evidence/sources" / name).rglob("*.py"))
    fixture = HERE / "uid_fixture"
    files.update(fixture.glob("*.py"))
    required = {"driver.py", "owner_controller.py"}
    if not required <= {p.name for p in fixture.glob("*.py")}:
        raise RuntimeError("fixed native UID fixture sources are not ready")
    with tempfile.TemporaryDirectory(prefix="ases4-uid-context-") as temporary:
        context = Path(temporary)
        hashes = {}
        for source in sorted(files):
            if source.is_symlink() or not source.is_file():
                raise RuntimeError("unexpected runtime source: " + str(source))
            relative = source.relative_to(REPO)
            destination = context / "src" / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            hashes[str(relative)] = sha(destination.read_bytes())
        dockerfile = fixture / "Dockerfile"
        shutil.copyfile(dockerfile, context / "Dockerfile")
        (context / ".dockerignore").write_text("**/__pycache__\n**/*.pyc\n")
        facts.update(context_sources=hashes, dockerfile_sha256=sha(dockerfile.read_bytes()),
                     source_commit=subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                                                  check=True, capture_output=True, text=True).stdout.strip())
        built = docker(["build", "--network=none", "--tag", tag, str(context)], build=True)
        facts["build"] = built
        if built["exit"]:
            (out / "failure.json").write_text(json.dumps(facts, indent=2) + "\n")
            raise RuntimeError("bounded native UID image build failed; exact output retained")
    image = docker(["image", "inspect", tag, "--format", "{{.Id}}"])
    facts["image"] = image
    run = docker(["run", "--rm", "--name", task, "--label", "org.ases4.uid-task=" + task,
                  "--network=none", "--cpus=1", "--memory=512m", "--pids-limit=32",
                  "--cap-drop=ALL", "--cap-add=CHOWN", "--cap-add=DAC_OVERRIDE",
                  "--cap-add=SETUID", "--cap-add=SETGID", "--security-opt=no-new-privileges", tag])
    facts["run"] = run
    if run["exit"]:
        inspection = docker(["container", "inspect", task, "--format",
                             '{{ index .Config.Labels "org.ases4.uid-task" }}|{{.Id}}'], timeout=10)
        facts["exact_container_inspection"] = inspection
        if inspection["exit"] == 0 and inspection["stdout"].split("|", 1)[0] == task:
            facts["exact_container_cleanup"] = docker(["container", "rm", "--force", task], timeout=15)
        facts["completed_task_image_cleanup"] = docker(["image", "rm", tag], timeout=30)
        (out / "failure.json").write_text(json.dumps(facts, indent=2) + "\n")
        raise RuntimeError("native UID run failed; exact output retained")
    raw = json.loads(run["stdout"])
    raw["outer"] = facts
    raw["outer"]["ended_ns"] = time.time_ns()
    raw["outer"]["completed_task_image_cleanup"] = docker(["image", "rm", tag], timeout=30)
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    print(json.dumps(dict(output=str(out), image_id=image["stdout"].strip(),
                          runtime_sources=len(hashes), status=raw.get("status", raw.get("execution")))))


if __name__ == "__main__": main()
