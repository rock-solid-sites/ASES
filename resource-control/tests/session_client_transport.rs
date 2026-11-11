//! Synthetic AF_UNIX transport fault histories for the fresh resource-session
//! client. These fixtures test client interpretation and retry behavior only;
//! they are not a native gateway or worker and prove no launch result.
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::io::{Read, Write};
use std::os::unix::net::UnixListener;
use std::os::unix::process::ExitStatusExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Output};
use std::thread;
use std::time::{Duration, Instant};

const JOB: &str = "transport-job";
const LAUNCH: &str = "transport-launch";

#[derive(Clone, Debug)]
enum Reply {
    Drop,
    Bytes(Vec<u8>),
    Trickle { bytes: Vec<u8>, interval: Duration },
}

#[derive(Debug)]
struct ServerCapture {
    accepted_connections: usize,
    raw_requests: Vec<String>,
    server_reply: Option<Vec<u8>>,
    server_write_errors: Vec<String>,
    reply_bytes_attempted: usize,
}

struct FaultServer {
    socket: PathBuf,
    listener: UnixListener,
    reply: Reply,
}

impl FaultServer {
    fn bind(dir: &Path, reply: Reply) -> Self {
        let socket = dir.join("fault.sock");
        let listener = UnixListener::bind(&socket).unwrap();
        listener.set_nonblocking(true).unwrap();
        Self { socket, listener, reply }
    }

    fn start(self, no_retry_window: Duration) -> (PathBuf, thread::JoinHandle<ServerCapture>) {
        let path = self.socket.clone();
        let handle = thread::spawn(move || {
            let hard_until = Instant::now() + Duration::from_secs(8);
            let mut monitor_until = None;
            let mut accepted_connections = 0;
            let mut raw_requests = Vec::new();
            let mut server_reply = None;
            let mut server_write_errors = Vec::new();
            let mut reply_bytes_attempted = 0;
            let mut first_handled = false;
            while Instant::now() < monitor_until.unwrap_or(hard_until) {
                match self.listener.accept() {
                    Ok((mut stream, _)) => {
                        accepted_connections += 1;
                        if !first_handled {
                            first_handled = true;
                            stream.set_read_timeout(Some(Duration::from_secs(2))).unwrap();
                            stream.set_write_timeout(Some(Duration::from_secs(2))).unwrap();
                            let mut bytes = Vec::new();
                            let _ = stream.read_to_end(&mut bytes);
                            raw_requests.push(String::from_utf8_lossy(&bytes).into_owned());
                            match &self.reply {
                                Reply::Drop => {}
                                Reply::Bytes(bytes) => {
                                    server_reply = Some(bytes.clone());
                                    reply_bytes_attempted = bytes.len();
                                    if let Err(error) = stream.write_all(bytes) {
                                        server_write_errors.push(error.to_string());
                                    }
                                }
                                Reply::Trickle { bytes, interval } => {
                                    server_reply = Some(bytes.clone());
                                    for byte in bytes {
                                        reply_bytes_attempted += 1;
                                        if let Err(error) = stream.write_all(std::slice::from_ref(byte)) {
                                            server_write_errors.push(error.to_string());
                                            break;
                                        }
                                        thread::sleep(*interval);
                                    }
                                }
                            }
                            drop(stream);
                            monitor_until = Some(Instant::now() + no_retry_window);
                            // Continue watching the listening socket after the
                            // first complete request so a hidden reconnect is
                            // counted as a second accepted connection.
                        } else {
                            let _ = stream.shutdown(std::net::Shutdown::Both);
                        }
                    }
                    Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => thread::sleep(Duration::from_millis(5)),
                    Err(_) => break,
                }
                // Once the one bounded client call has returned, the listener
                // remains open until monitor_until to catch automatic retries.
            }
            ServerCapture { accepted_connections, raw_requests, server_reply,
                server_write_errors, reply_bytes_attempted }
        });
        (path, handle)
    }
}

fn client(args: &[&str]) -> Output {
    Command::new(env!("CARGO_BIN_EXE_resource-session"))
        .args(args)
        .output()
        .expect("run resource-session binary")
}

fn code(output: &Output) -> Option<i32> { output.status.code() }

fn outcome_diagnostic(output: &Output) -> Value {
    for bytes in [&output.stdout, &output.stderr] {
        for line in String::from_utf8_lossy(bytes).lines() {
            if let Ok(value) = serde_json::from_str::<Value>(line) {
                if value.get("outcome").is_some() { return value; }
            }
        }
    }
    panic!("no machine-readable outcome in stdout/stderr: stdout={:?}, stderr={:?}",
        String::from_utf8_lossy(&output.stdout), String::from_utf8_lossy(&output.stderr));
}

fn source_hashes() -> Value {
    let root = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let mut result = serde_json::Map::new();
    for relative in ["src/bin/resource-session.rs", "tests/session_client_transport.rs",
        "../docs/research/phase-ii-local-execution/CLIENT-PACKET.md"] {
        if let Ok(bytes) = fs::read(root.join(relative)) {
            result.insert(relative.into(), json!(format!("{:x}", Sha256::digest(bytes))));
        }
    }
    Value::Object(result)
}

fn persist(name: &str, record: Value) {
    if let Some(path) = std::env::var_os("ASES_SESSION_TRANSPORT_EVIDENCE_DIR") {
        let dir = PathBuf::from(path);
        fs::create_dir_all(&dir).unwrap();
        fs::write(dir.join(name), serde_json::to_vec_pretty(&record).unwrap()).unwrap();
    }
}

fn captured_server(dir: &Path, reply: Reply) -> (PathBuf, thread::JoinHandle<ServerCapture>) {
    FaultServer::bind(dir, reply).start(Duration::from_millis(250))
}

fn assert_one_request(capture: &ServerCapture, expected: &Value) {
    assert_eq!(capture.accepted_connections, 1, "exactly one accepted client connection: {capture:?}");
    assert_eq!(capture.raw_requests.len(), 1, "exactly one complete request: {capture:?}");
    let parsed: Value = serde_json::from_str(&capture.raw_requests[0]).unwrap();
    assert_eq!(&parsed, expected, "full captured wire request");
}

fn effect_request(socket: &Path) -> Vec<String> {
    vec![socket.display().to_string(), "launch".into(), JOB.into(), LAUNCH.into(), "17".into()]
}

fn borrowed(args: &[String]) -> Vec<&str> { args.iter().map(String::as_str).collect() }

#[test]
fn effect_request_lost_reply_is_unknown_and_never_retried() {
    let dir = tempfile::tempdir().unwrap();
    let (socket, server) = captured_server(dir.path(), Reply::Drop);
    let args = effect_request(&socket);
    let output = client(&borrowed(&args));
    let capture = server.join().unwrap();
    let diagnostic = outcome_diagnostic(&output);
    assert_eq!(code(&output), Some(4));
    assert_eq!(diagnostic["outcome"], "outcome_unknown");
    assert_one_request(&capture, &json!({
        "op":"local_launch","job_id":JOB,"launch_id":LAUNCH,"expected_catalog":17
    }));
    let record = json!({"source_sha256":source_hashes(),"request_args":args,
        "client_stdout":String::from_utf8_lossy(&output.stdout),
        "client_stderr":String::from_utf8_lossy(&output.stderr),"exit_code":code(&output),
        "exit_signal":output.status.signal(),"client_diagnostic":diagnostic,
        "accepted_connections":capture.accepted_connections,"raw_requests":capture.raw_requests,
        "server_reply":capture.server_reply,"retry_observation_ms":250});
    persist("effect-lost-reply.json", record);
}

#[test]
fn truncated_reply_is_unknown_after_exactly_one_captured_request() {
    let dir = tempfile::tempdir().unwrap();
    let partial = br#"{"ok":true,"result":{"state":"running"}"#.to_vec();
    let (socket, server) = captured_server(dir.path(), Reply::Bytes(partial.clone()));
    let args = effect_request(&socket);
    let output = client(&borrowed(&args));
    let capture = server.join().unwrap();
    let diagnostic = outcome_diagnostic(&output);
    assert_eq!(code(&output), Some(4));
    assert_eq!(diagnostic["outcome"], "outcome_unknown");
    assert_one_request(&capture, &json!({
        "op":"local_launch","job_id":JOB,"launch_id":LAUNCH,"expected_catalog":17
    }));
    persist("truncated-reply.json", json!({"source_sha256":source_hashes(),
        "request_args":args,"client_stdout":String::from_utf8_lossy(&output.stdout),
        "client_stderr":String::from_utf8_lossy(&output.stderr),"exit_code":code(&output),
        "client_diagnostic":diagnostic,"accepted_connections":capture.accepted_connections,
        "raw_requests":capture.raw_requests,"server_reply_bytes":partial}));
}

#[test]
fn response_deadline_expires_during_slow_trickle_and_does_not_retry() {
    let dir = tempfile::tempdir().unwrap();
    let trickle = b"{\"ok\":tr".to_vec();
    let (socket, server) = captured_server(dir.path(), Reply::Trickle {
        bytes: trickle.clone(), interval: Duration::from_millis(600),
    });
    let args = effect_request(&socket);
    let started = Instant::now();
    let output = client(&borrowed(&args));
    let elapsed_ms = started.elapsed().as_millis();
    let capture = server.join().unwrap();
    let diagnostic = outcome_diagnostic(&output);
    assert_eq!(code(&output), Some(4));
    assert_eq!(diagnostic["outcome"], "outcome_unknown");
    assert!(elapsed_ms < 4_500, "total response deadline should beat rolling per-read timeout; elapsed {elapsed_ms}ms");
    assert_one_request(&capture, &json!({
        "op":"local_launch","job_id":JOB,"launch_id":LAUNCH,"expected_catalog":17
    }));
    persist("slow-trickle-deadline.json", json!({"source_sha256":source_hashes(),
        "request_args":args,"client_stdout":String::from_utf8_lossy(&output.stdout),
        "client_stderr":String::from_utf8_lossy(&output.stderr),"exit_code":code(&output),
        "elapsed_ms":elapsed_ms,"client_diagnostic":diagnostic,
        "accepted_connections":capture.accepted_connections,"raw_requests":capture.raw_requests,
        "trickle_response_bytes":trickle,"reply_bytes_attempted":capture.reply_bytes_attempted,
        "server_write_errors":capture.server_write_errors,
        "server_reply_bytes":capture.server_reply,"retry_observation_ms":250}));
}

#[test]
fn unsupported_gateway_reply_shapes_are_unknown() {
    let dir = tempfile::tempdir().unwrap();
    let mut cases = Vec::new();
    for (label, reply) in [
        ("ok_true_without_result", br#"{"ok":true}"#.to_vec()),
        ("ok_false_without_string_error", br#"{"ok":false,"error":7}"#.to_vec()),
    ] {
        let case_dir = dir.path().join(label);
        fs::create_dir(&case_dir).unwrap();
        let (socket, server) = captured_server(&case_dir, Reply::Bytes(reply.clone()));
        let args = effect_request(&socket);
        let output = client(&borrowed(&args));
        let capture = server.join().unwrap();
        let diagnostic = outcome_diagnostic(&output);
        assert_eq!(code(&output), Some(4));
        assert_eq!(diagnostic["outcome"], "outcome_unknown");
        assert_one_request(&capture, &json!({
            "op":"local_launch","job_id":JOB,"launch_id":LAUNCH,"expected_catalog":17
        }));
        cases.push(json!({"label":label,"reply":reply,"args":args,
            "stdout":String::from_utf8_lossy(&output.stdout),
            "stderr":String::from_utf8_lossy(&output.stderr),"exit_code":code(&output),
            "diagnostic":diagnostic,"accepted_connections":capture.accepted_connections,
            "raw_requests":capture.raw_requests}));
    }
    persist("unsupported-reply-shapes.json", json!({"source_sha256":source_hashes(),"cases":cases}));
}

#[test]
fn oversized_reply_is_unknown_and_response_buffer_stays_bounded() {
    let dir = tempfile::tempdir().unwrap();
    let mut oversized = br#"{"ok":true,"result":""#.to_vec();
    oversized.extend(std::iter::repeat(b'x').take(9 * 1024));
    oversized.extend_from_slice(b"\"}");
    let (socket, server) = captured_server(dir.path(), Reply::Bytes(oversized.clone()));
    let args = effect_request(&socket);
    let output = client(&borrowed(&args));
    let capture = server.join().unwrap();
    let diagnostic = outcome_diagnostic(&output);
    assert_eq!(code(&output), Some(4));
    assert_eq!(diagnostic["outcome"], "outcome_unknown");
    assert!(String::from_utf8_lossy(&output.stdout).len() <= 8 * 1024,
        "oversized response must never be emitted on stdout");
    assert_one_request(&capture, &json!({
        "op":"local_launch","job_id":JOB,"launch_id":LAUNCH,"expected_catalog":17
    }));
    persist("oversized-reply.json", json!({"source_sha256":source_hashes(),
        "request_args":args,"client_stdout":String::from_utf8_lossy(&output.stdout),
        "client_stderr":String::from_utf8_lossy(&output.stderr),"exit_code":code(&output),
        "client_diagnostic":diagnostic,"accepted_connections":capture.accepted_connections,
        "raw_requests":capture.raw_requests,"server_reply_bytes":oversized.len()}));
}

#[test]
fn received_server_error_stays_distinct_from_unknown_transport_outcome() {
    let dir = tempfile::tempdir().unwrap();
    let server_reply = br#"{"ok":false,"error":"conflict after durable intent"}"#.to_vec();
    let (socket, server) = captured_server(dir.path(), Reply::Bytes(server_reply.clone()));
    let args = effect_request(&socket);
    let output = client(&borrowed(&args));
    let capture = server.join().unwrap();
    assert_eq!(code(&output), Some(3));
    let decoded: Value = serde_json::from_slice(&output.stdout).unwrap();
    assert_eq!(decoded, json!({"ok":false,"error":"conflict after durable intent"}));
    assert_ne!(decoded.get("outcome"), Some(&json!("outcome_unknown")));
    assert_one_request(&capture, &json!({
        "op":"local_launch","job_id":JOB,"launch_id":LAUNCH,"expected_catalog":17
    }));
    persist("received-server-error.json", json!({"source_sha256":source_hashes(),
        "request_args":args,"client_stdout":String::from_utf8_lossy(&output.stdout),
        "client_stderr":String::from_utf8_lossy(&output.stderr),"exit_code":code(&output),
        "accepted_connections":capture.accepted_connections,"raw_requests":capture.raw_requests,
        "server_reply":server_reply,"decoded_response":decoded}));
}

#[test]
fn invalid_selectors_and_command_or_pid_extras_are_rejected_before_connect() {
    let dir = tempfile::tempdir().unwrap();
    let server = FaultServer::bind(dir.path(), Reply::Drop);
    let socket = server.socket.clone();
    let mut cases = Vec::new();
    let invalid_args = vec![
        vec![socket.display().to_string(), "resume".into(), "bad job".into(), LAUNCH.into()],
        vec![socket.display().to_string(), "launch".into(), JOB.into(), LAUNCH.into(), "-1".into()],
        vec![socket.display().to_string(), "launch".into(), JOB.into(), LAUNCH.into(), "17".into(), "/bin/true".into()],
        vec![socket.display().to_string(), "launch".into(), JOB.into(), LAUNCH.into(), "17".into(), "--pid".into(), "123".into()],
        vec![socket.display().to_string(), "stop".into(), JOB.into(), LAUNCH.into(), "stop-a".into(), "--command".into(), "/bin/true".into()],
    ];
    for args in invalid_args {
        let output = client(&borrowed(&args));
        assert_eq!(code(&output), Some(2), "invalid CLI input: {args:?}");
        let diagnostic = outcome_diagnostic(&output);
        assert_eq!(diagnostic["ok"], false);
        assert_ne!(diagnostic["outcome"], "outcome_unknown");
        cases.push(json!({"args":args,"stdout":String::from_utf8_lossy(&output.stdout),
            "stderr":String::from_utf8_lossy(&output.stderr),"exit_code":code(&output),
            "diagnostic":diagnostic}));
    }
    let mut accepted_connections = 0;
    let until = Instant::now() + Duration::from_millis(250);
    while Instant::now() < until {
        match server.listener.accept() {
            Ok((mut stream, _)) => {
                accepted_connections += 1;
                let mut request = Vec::new();
                let _ = stream.read_to_end(&mut request);
                cases.push(json!({"unexpected_wire_request":String::from_utf8_lossy(&request)}));
            }
            Err(error) if error.kind() == std::io::ErrorKind::WouldBlock => thread::sleep(Duration::from_millis(5)),
            Err(error) => panic!("fault listener accept failed: {error}"),
        }
    }
    assert_eq!(accepted_connections, 0, "all invalid CLI cases must be rejected before connect");
    persist("invalid-input-no-connect.json", json!({"source_sha256":source_hashes(),
        "cases":cases,"accepted_connections":accepted_connections}));
}
