import ctypes
import json
import os
import signal
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURE = os.path.join(HERE, 'fixture')
TARGET = os.path.join(FIXTURE, 'sentinel.txt')
ALIAS = os.path.join(FIXTURE, 'alias.txt')
CONTENT = b'authority-loss-sentinel-v1'
SYS_CREATE, SYS_ADD, SYS_RESTRICT = 444, 445, 446
READ_FILE, READ_DIR = 1 << 2, 1 << 3

# Process code is deliberately stdlib-only and is exec'd as separate actors.
MEDIATOR = r'''import json, os, socket, sys, time
sock = socket.socket(fileno=int(sys.argv[1]))
target = sys.argv[2]
for request in range(2):
    data = bytearray()
    while True:
        c = sock.recv(1)
        if not c or c == b'|': break
        data += c
    if not data: break
    fd = os.open(target, os.O_RDONLY)
    try: content = os.read(fd, 256)
    finally: os.close(fd)
    sock.sendall(b'OK ' + content + b'|')
    print(json.dumps({'pid':os.getpid(),'request':request+1,'authorized_from_cached_grant':True,'bytes':len(content)}, sort_keys=True), flush=True)
'''
HOLDER = r'''import os, sys, time
print('HOLDER_READY %d %d' % (os.getpid(), time.monotonic_ns()), flush=True)
time.sleep(30)
'''
WORKER = r'''import json, os, signal, socket, sys, time
TARGET, ALIAS, FD = sys.argv[1], sys.argv[2], int(sys.argv[3])
s = socket.socket(fileno=FD)
def line():
    b=bytearray()
    while True:
        c=s.recv(1)
        if not c or c==b'|': break
        b += c
    return bytes(b)
s.sendall(b'READ|')
first=line()
print(json.dumps({'event':'baseline_read','pid':os.getpid(),'time_ns':time.monotonic_ns(),'reply':first.decode('utf-8','replace')},sort_keys=True),flush=True)
trigger=__import__('threading').Event()
def go(sig, frame):
    global signal_ns
    signal_ns=time.monotonic_ns()
    trigger.set()
signal.signal(signal.SIGUSR1,go)
trigger.wait(5)
start=time.monotonic_ns()
# Volatile CPU-only work: no files, sockets, or other effect during this interval.
x=0
until=time.monotonic()+0.08
while time.monotonic()<until: x=(x*1664525+1013904223)&0xffffffff
cpu_end=time.monotonic_ns()
try:
    s.sendall(b'READ|')
    second=line()
except OSError as e: second=b'IOERROR:'+str(e.errno).encode()
alias_results={}
for label,path in [('direct_target',TARGET),('symlink_alias',ALIAS)]:
    try:
        fd=os.open(path,os.O_RDONLY)
        try: alias_results[label]={'result':'allowed','bytes':os.read(fd,256).decode('utf-8','replace')}
        finally: os.close(fd)
    except OSError as e: alias_results[label]={'result':'denied','errno':e.errno,'detail':e.strerror}
print(json.dumps({'event':'post_loss','pid':os.getpid(),'signal_ns':signal_ns,'cpu_start_ns':start,'cpu_end_ns':cpu_end,'cpu_iterations':x,'second_reply':second.decode('utf-8','replace'),'second_has_protected_bytes':'authority-loss-sentinel-v1' in second.decode('utf-8','replace'),'paths':alias_results},sort_keys=True),flush=True)
'''


def add_allow_rule(libc, ruleset, path):
    if not os.path.exists(path):
        return
    fd = os.open(path, getattr(os, 'O_PATH', 0o10000000) | os.O_CLOEXEC)
    try:
        class Rule(ctypes.Structure):
            _fields_ = [('allowed_access', ctypes.c_uint64), ('parent_fd', ctypes.c_int)]
        rights = READ_FILE if os.path.isfile(path) else READ_FILE | READ_DIR
        rule = Rule(rights, fd)
        if libc.syscall(SYS_ADD, ctypes.c_int(ruleset), ctypes.c_int(1), ctypes.byref(rule), ctypes.c_uint(0)) != 0:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e), path)
    finally:
        os.close(fd)


def confine_before_exec():
    libc = ctypes.CDLL(None, use_errno=True)
    attr = ctypes.c_uint64(READ_FILE | READ_DIR)
    ruleset = libc.syscall(SYS_CREATE, ctypes.byref(attr), ctypes.c_size_t(ctypes.sizeof(attr)), ctypes.c_uint(0))
    if ruleset < 0:
        e = ctypes.get_errno()
        raise OSError(e, os.strerror(e), 'landlock_create_ruleset')
    try:
        for path in ('/usr', '/lib', '/lib64', '/etc/ld.so.cache'):
            add_allow_rule(libc, ruleset, path)
        if libc.prctl(38, 1, 0, 0, 0) != 0:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e), 'PR_SET_NO_NEW_PRIVS')
        if libc.syscall(SYS_RESTRICT, ctypes.c_int(ruleset), ctypes.c_uint(0)) != 0:
            e = ctypes.get_errno()
            raise OSError(e, os.strerror(e), 'landlock_restrict_self')
    finally:
        os.close(ruleset)


def read_event(pipe):
    line = pipe.readline()
    if not line:
        raise RuntimeError('worker exited before baseline event')
    return json.loads(line)


def launch_worker(client):
    p = subprocess.Popen([sys.executable, '-S', '-c', WORKER, TARGET, ALIAS, str(client.fileno())],
                         pass_fds=(client.fileno(),), preexec_fn=confine_before_exec,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, close_fds=True)
    client.close()
    return p


def one_run(separate_mediator):
    client_parent, client_child = socket.socketpair()
    # H is a standalone disposable process in both profiles. In safe profile H=M and
    # owns the only mediator endpoint. In the mutant H is separate from surviving M.
    if separate_mediator:
        holder = subprocess.Popen([sys.executable, '-S', '-c', HOLDER], stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, close_fds=True)
        mediator = subprocess.Popen([sys.executable, '-S', '-c', MEDIATOR, str(client_child.fileno()), TARGET],
                                    pass_fds=(client_child.fileno(),), stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, close_fds=True)
        holder_line = holder.stdout.readline().strip()
        mediator_pid = mediator.pid
    else:
        holder = subprocess.Popen([sys.executable, '-S', '-c', MEDIATOR, str(client_child.fileno()), TARGET],
                                  pass_fds=(client_child.fileno(),), stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, close_fds=True)
        mediator = holder
        holder_line = 'H_EQUALS_M pid=%d' % holder.pid
        mediator_pid = holder.pid
    client_child.close()
    worker = launch_worker(client_parent)
    baseline = read_event(worker.stdout)
    if baseline.get('event') != 'baseline_read' or 'authority-loss-sentinel-v1' not in baseline.get('reply', ''):
        raise RuntimeError('nonvacuous baseline failed: '+repr(baseline))
    kill_ns = time.monotonic_ns()
    os.kill(holder.pid, signal.SIGKILL)
    holder_status = holder.wait(timeout=2)
    loss_ns = time.monotonic_ns()
    os.kill(worker.pid, signal.SIGUSR1)
    post = read_event(worker.stdout)
    tail = worker.stdout.read()
    worker_status = worker.wait(timeout=3)
    mediator_status = None
    mediator_trace = ''
    if separate_mediator:
        mediator_status = mediator.poll()
        if mediator_status is None:
            mediator.kill()
            mediator_status = mediator.wait(timeout=2)
        mediator_trace = mediator.stdout.read()
    else:
        mediator_status = holder_status
        mediator_trace = holder.stdout.read()
    return {'profile':'separate_H_stale_grant_mutant' if separate_mediator else 'H_equals_M_safe_candidate',
            'holder_pid':holder.pid,'holder_ready':holder_line,'holder_kill_requested_ns':kill_ns,
            'holder_wait_reaped_ns':loss_ns,'holder_returncode':holder_status,
            'mediator_pid':mediator_pid,'mediator_returncode_after_cleanup':mediator_status,
            'worker_pid':worker.pid,'worker_returncode':worker_status,'baseline':baseline,'post_loss':post,
            'worker_extra_output':tail,'mediator_trace':mediator_trace,
            'violation_detected':bool(separate_mediator and post.get('second_has_protected_bytes'))}


def main():
    os.makedirs(FIXTURE, mode=0o700, exist_ok=True)
    with open(TARGET, 'wb') as f: f.write(CONTENT)
    try: os.unlink(ALIAS)
    except FileNotFoundError: pass
    os.symlink('sentinel.txt', ALIAS)
    started = time.monotonic_ns()
    safe = one_run(False)
    mutant = one_run(True)
    result={'status':'completed','python':sys.version,'kernel':__import__('platform').release(),
            'fixture':FIXTURE,'sentinel_sha256':__import__('hashlib').sha256(CONTENT).hexdigest(),
            'safe_candidate':safe,'stale_grant_fault_control':mutant,
            'safe_candidate_pass': (safe['baseline']['reply'].startswith('OK ') and
                not safe['post_loss']['second_has_protected_bytes'] and
                safe['post_loss']['cpu_iterations']>0 and
                safe['holder_returncode']==-signal.SIGKILL and safe['holder_wait_reaped_ns']<safe['post_loss']['signal_ns'] and
                all(v.get('result')=='denied' for v in safe['post_loss']['paths'].values())),
            'fault_control_detected':mutant['violation_detected'],'elapsed_ns':time.monotonic_ns()-started}
    print(json.dumps(result,sort_keys=True,indent=2))
    if not result['safe_candidate_pass'] or not result['fault_control_detected']:
        return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
