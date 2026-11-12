#!/usr/bin/env python3
"""Run the bounded native recovery UID fixture in the pinned local image."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import traceback

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BASE_ID = "sha256:b5ba49a53a9c5ad0d0fc3c2c925773589e0d8912cd8077eca91af0bb4ab5e335"
BASE_SIZE = 119614344
BASE_DRIVER = "/opt/probe/driver.py"
CONTAINER_DRIVER = "/opt/owned-src/docs/research/phase-ii-native-recovery-uid/fixture/driver.py"
SOCKET = "unix:///var/run/docker.sock"
LABEL = "org.ases4.uid-recovery-task"
UNSET_DOCKER_ENV = (
    "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_TLS", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH",
)


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def docker_command(outer: dict, arguments: list[str], *, timeout: int = 300) -> dict:
    """Execute and record one explicit local-socket Docker CLI command."""
    env = dict(os.environ)
    cleared = []
    for key in UNSET_DOCKER_ENV:
        if key in env:
            cleared.append(key)
        env.pop(key, None)
    argv = ["docker", f"--host={SOCKET}", *arguments]
    started_ns = time.time_ns()
    try:
        process = subprocess.run(argv, env=env, capture_output=True, text=True,
                                 timeout=timeout, check=False)
        result = {"argv": argv, "exit": process.returncode, "stdout": process.stdout,
                  "stderr": process.stderr, "started_ns": started_ns,
                  "finished_ns": time.time_ns(), "cleared_docker_env": cleared}
    except subprocess.TimeoutExpired as error:
        stdout = error.stdout or ""
        stderr = error.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        result = {"argv": argv, "exit": 124, "stdout": stdout, "stderr": stderr,
                  "started_ns": started_ns, "finished_ns": time.time_ns(),
                  "timed_out": True, "cleared_docker_env": cleared}
    except OSError as error:
        result = {"argv": argv, "exit": 127, "stdout": "",
                  "stderr": f"{type(error).__name__}: {error}",
                  "started_ns": started_ns, "finished_ns": time.time_ns(),
                  "cleared_docker_env": cleared}
    outer.setdefault("docker_commands", []).append(result)
    return result


def runtime_sources() -> set[Path]:
    """Reuse run_uid.py's explicit runtime set and add this recovery fixture."""
    files: set[Path] = set()
    runtime = {
        "phase-ii-native-ownership": (
            "native_owner.py", "owner_cli.py", "native_sink.py", "unix_transport.py", "probe.py",
        ),
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
        source_root = REPO / "docs/research/phase-i-sol-integration/evidence/sources" / name
        files.update(path for path in source_root.rglob("*.py") if path.is_file() and not path.is_symlink())
    files.update((HERE.parent / "phase-ii-native-publication-reconcile" / "reconcile.py",))
    local_observation = HERE.parent / "phase-ii-native-local-observation"
    files.update((local_observation / "observe_local.py", local_observation / "test_sink_gate.py"))
    fixture = HERE / "fixture"
    files.update(fixture / name for name in ("driver.py", "owner_controller.py", "worker.py"))
    return files


def stage_sources(destination: Path) -> tuple[dict, list[dict]]:
    files = runtime_sources()
    required_fixture = {"driver.py", "owner_controller.py", "worker.py"}
    present_fixture = {path.name for path in files if path.parent == HERE / "fixture" and path.is_file()}
    missing = required_fixture - present_fixture
    if missing:
        raise FileNotFoundError("recovery fixture is not ready; missing: " + ", ".join(sorted(missing)))
    manifest = {}
    directories: dict[Path, None] = {}
    for source in sorted(files):
        if source.is_symlink() or not source.is_file():
            raise RuntimeError("unexpected or missing runtime source: " + str(source))
        relative = source.relative_to(REPO)
        target = destination / relative
        target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        os.chmod(target, 0o644)
        manifest[relative.as_posix()] = {
            "sha256": sha(target.read_bytes()), "size": target.stat().st_size,
            "mode": "0644", "container_uid": 0, "container_gid": 0,
        }
        parent = target.parent
        while parent != destination.parent:
            directories[parent] = None
            if parent == destination:
                break
            parent = parent.parent
    for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        os.chmod(directory, 0o755)
    directory_manifest = [
        {"path": path.relative_to(destination).as_posix(), "mode": "0755",
         "container_uid": 0, "container_gid": 0}
        for path in sorted(directories, key=lambda item: item.as_posix())
    ]
    return manifest, directory_manifest


def verify_staged_sources_against_commit(commit: str, manifest: dict) -> list[dict]:
    """Require every staged byte to be present unchanged at the recorded commit."""
    checks = []
    for relative, staged in sorted(manifest.items()):
        argv = ["git", "show", f"{commit}:{relative}"]
        try:
            process = subprocess.run(argv, cwd=REPO, capture_output=True, check=False)
            record = {"argv": argv, "exit": process.returncode,
                      "stderr": process.stderr.decode(errors="replace")}
            if process.returncode == 0:
                git_sha = sha(process.stdout)
                record.update(git_sha256=git_sha, staged_sha256=staged["sha256"],
                              matches=git_sha == staged["sha256"])
            else:
                record.update(git_sha256=None, staged_sha256=staged["sha256"], matches=False)
        except OSError as error:
            record = {"argv": argv, "exit": 127,
                      "stderr": f"{type(error).__name__}: {error}",
                      "git_sha256": None, "staged_sha256": staged["sha256"], "matches": False}
        checks.append(record)
    return checks


def parse_image_inspection(command: dict) -> dict:
    if command["exit"] != 0:
        raise RuntimeError("pinned base image inspect failed")
    try:
        value = json.loads(command["stdout"])
        image = value[0]
    except (json.JSONDecodeError, IndexError, TypeError) as error:
        raise RuntimeError("Docker returned an invalid image inspection") from error
    entrypoint = image.get("Config", {}).get("Entrypoint")
    graph = image.get("GraphDriver", {}).get("Name")
    facts = {"Id": image.get("Id"), "Size": image.get("Size"),
             "GraphDriver": graph, "Entrypoint": entrypoint,
             "RepoTags": image.get("RepoTags", [])}
    if facts["Id"] != BASE_ID or facts["Size"] != BASE_SIZE or graph != "vfs":
        raise RuntimeError("pinned image identity, size, or VFS storage changed")
    if not isinstance(entrypoint, list) or BASE_DRIVER not in entrypoint:
        raise RuntimeError("pinned image no longer contains its expected original driver entrypoint")
    return facts


def parse_driver_output(stdout: str) -> dict:
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise ValueError("container produced no driver JSON frame")
    value = json.loads(lines[-1])
    if not isinstance(value, dict):
        raise ValueError("final driver output is not a JSON object")
    return value


def run(args) -> tuple[dict, int]:
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    task = f"ases4-native-recovery-uid-{os.getpid()}-{time.time_ns()}"
    outer = {
        "schema": "ases4-native-recovery-uid-runner-v1",
        "started_ns": time.time_ns(), "task": task, "label_key": LABEL,
        "label_value": task, "image_id": BASE_ID, "docker_socket": SOCKET,
        "docker_environment_cleared": list(UNSET_DOCKER_ENV),
        "container_id": None, "container_name": task,
        "container_constraints": {
            "network": "none", "cpus": 1, "memory": "512m", "pids_limit": 32,
            "cap_drop": ["ALL"], "cap_add": ["CHOWN", "DAC_OVERRIDE", "SETUID", "SETGID"],
            "no_new_privileges": True, "user": "0:0", "mounts": [], "ports": [],
        },
        "docker_commands": [], "source_commit": None, "staged_sources": {},
        "staged_directories": [], "driver_stdout": "", "driver_stderr": "",
        "driver_result": None, "container_inspection": None, "cleanup": None,
    }
    raw = {"schema": "ases4-native-recovery-uid-v1", "status": "FAIL", "cases": {}, "outer": outer}
    container_id = None
    temp_context = None
    try:
        image_inspect = docker_command(outer, ["image", "inspect", BASE_ID])
        outer["image_inspection_command"] = image_inspect
        outer["image"] = parse_image_inspection(image_inspect)
        outer["source_commit"] = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO, check=True,
            capture_output=True, text=True,
        ).stdout.strip()

        with tempfile.TemporaryDirectory(prefix="ases4-native-recovery-uid-") as temporary:
            temp_context = Path(temporary)
            source_root = temp_context / "owned-src"
            source_root.mkdir(mode=0o755)
            manifest, directory_manifest = stage_sources(source_root)
            outer["staged_sources"] = manifest
            outer["staged_directories"] = directory_manifest
            source_checks = verify_staged_sources_against_commit(outer["source_commit"], manifest)
            outer["source_commit_checks"] = source_checks
            if not all(item.get("matches") is True and item.get("exit") == 0
                       for item in source_checks):
                raise RuntimeError("staged runtime files differ from the recorded source commit")
            outer["source_commit_verified"] = True
            create_args = [
                "container", "create", "--name", task,
                "--label", f"{LABEL}={task}", "--network=none",
                "--cpus=1", "--memory=512m", "--pids-limit=32",
                "--cap-drop=ALL", "--cap-add=CHOWN", "--cap-add=DAC_OVERRIDE",
                "--cap-add=SETUID", "--cap-add=SETGID", "--security-opt=no-new-privileges",
                "--user=0:0", "--entrypoint", "python", BASE_ID,
                "-I", "-B", CONTAINER_DRIVER,
            ]
            created = docker_command(outer, create_args, timeout=60)
            if created["exit"] != 0:
                raise RuntimeError("failed to create the single labeled recovery container")
            container_id = created["stdout"].strip() or None
            outer["container_id"] = container_id
            if not container_id:
                raise RuntimeError("Docker create returned no container ID")
            copy_result = docker_command(outer, ["cp", str(source_root) + "/.",
                                                  container_id + ":/opt/owned-src/"], timeout=120)
            outer["copy_result"] = copy_result
            if copy_result["exit"] != 0:
                raise RuntimeError("failed to copy staged runtime source into the task container")

            start_result = docker_command(outer, ["start", "--attach", container_id], timeout=args.timeout)
            outer["start_attach"] = start_result
            outer["driver_stdout"] = start_result["stdout"]
            outer["driver_stderr"] = start_result["stderr"]
            try:
                outer["driver_result"] = parse_driver_output(start_result["stdout"])
            except (json.JSONDecodeError, ValueError) as error:
                outer["driver_parse_error"] = f"{type(error).__name__}: {error}"

            inspected = docker_command(outer, ["container", "inspect", container_id], timeout=30)
            outer["container_inspect_command"] = inspected
            if inspected["exit"] == 0:
                try:
                    item = json.loads(inspected["stdout"])[0]
                    state = item.get("State", {})
                    labels = item.get("Config", {}).get("Labels", {}) or {}
                    outer["container_inspection"] = {
                        "Id": item.get("Id"), "Name": item.get("Name"),
                        "label": labels.get(LABEL), "State": state,
                    }
                except (json.JSONDecodeError, IndexError, TypeError) as error:
                    outer["container_inspection_error"] = f"{type(error).__name__}: {error}"
    except BaseException as error:
        outer["runner_error"] = {"type": type(error).__name__, "message": str(error),
                                 "traceback": traceback.format_exc()}
    finally:
        cleanup_target = container_id or task
        inspect_for_cleanup = docker_command(outer, ["container", "inspect", cleanup_target], timeout=30)
        if inspect_for_cleanup["exit"] == 0:
            try:
                item = json.loads(inspect_for_cleanup["stdout"])[0]
                labels = item.get("Config", {}).get("Labels", {}) or {}
                inspected_id = item.get("Id")
                inspected_name = item.get("Name")
                inspected_label = labels.get(LABEL)
                cleanup_identity_matches = (
                    isinstance(inspected_id, str)
                    and (container_id is None or inspected_id == container_id)
                    and inspected_name == "/" + task and inspected_label == task
                )
                if container_id is None and cleanup_identity_matches:
                    container_id = inspected_id
                    outer["container_id"] = inspected_id
                if outer.get("container_inspection") is None and cleanup_identity_matches:
                    outer["container_inspection"] = {
                        "Id": inspected_id, "Name": inspected_name,
                        "label": inspected_label, "State": item.get("State", {}),
                    }
            except (json.JSONDecodeError, IndexError, TypeError):
                cleanup_identity_matches = False
        else:
            cleanup_identity_matches = False
        outer["cleanup_preflight_inspection"] = inspect_for_cleanup
        if container_id is not None:
            if cleanup_identity_matches:
                outer["cleanup"] = docker_command(
                    outer, ["container", "rm", "--force", container_id], timeout=30)
                if outer["cleanup"]["exit"] != 0:
                    raw["status"] = "FAIL"
                    outer["cleanup_error"] = "exact labeled task container removal failed"
            else:
                outer["cleanup"] = {"skipped": True,
                                    "reason": "exact ID, name, and task label did not all match",
                                    "inspection": inspect_for_cleanup}
        outer["ended_ns"] = time.time_ns()

    driver = outer.get("driver_result")
    if isinstance(driver, dict):
        raw.update(driver)
        raw["outer"] = outer
    success = (not outer.get("runner_error") and isinstance(driver, dict)
               and driver.get("status") == "PASS"
               and outer.get("start_attach", {}).get("exit") == 0
               and isinstance(outer.get("container_inspection"), dict)
               and outer["container_inspection"].get("Id") == container_id
               and outer["container_inspection"].get("label") == task
               and outer["container_inspection"].get("State", {}).get("ExitCode") == 0
               and isinstance(outer.get("cleanup"), dict)
               and outer["cleanup"].get("exit") == 0)
    raw["status"] = "PASS" if success else "FAIL"
    outer["runner_status"] = raw["status"]
    raw["outer"] = outer
    (out / "raw.json").write_text(json.dumps(raw, sort_keys=True, indent=2) + "\n")
    return raw, 0 if success else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=int, default=300,
                        help="maximum seconds for one container start/attach (default: 300)")
    args = parser.parse_args()
    if args.timeout < 1 or args.timeout > 1800:
        parser.error("--timeout must be between 1 and 1800 seconds")
    raw, status = run(args)
    print(json.dumps({"status": raw["status"], "raw": str(args.out.resolve() / "raw.json"),
                      "container_id": raw["outer"].get("container_id")}, sort_keys=True))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
