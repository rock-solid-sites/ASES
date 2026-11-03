# F3 review evidence preservation

The first policy observation's stdout was printed to the session tool transcript and was **not saved as a raw file**. The first native run's traceback was likewise not separately saved; its result is recorded in the first verdict. Neither is represented here as a retained original output. `policy-rerun.*` is a **second independent execution** of the same policy probe, and `landlock-rerun.*` is a second execution of the direct syscall probe. Their stdout, stderr and exit status are retained separately. PIDs naturally differ. The second policy run again observed authorized positive write, read through sealed Q, and unsafe-ceiling write. The second syscall probe again returned ABI -1, errno 38.

`policy_test_original.py` is the exact first script, including its original absolute `/tmp` paths. `lifecycle/l5/test_ancestor.py` is the exact modified L5 copy it produced; `l5_integrated.py`, `l1.py`, the checked-in L4 `lab` and `raw-run.json` are the copied inputs. The L4 fixture and raw are historical checked-in inputs, not a fresh L4 run. `policy_test_portable.py` changes only path selection to `ASES_F3_EVIDENCE_COPY`; it retains the original script's operations and creates its mutated source inside a disposable copy. Both the script and copied source override confinement for this test. The bounded policy results do not prove OS isolation or an actual L4 recovery.

From this evidence directory, run the following; the script needs Python 3 and a POSIX environment. It writes only under the newly created temporary directory:

```sh
copy=$(mktemp -d /tmp/ases-f3-repro-XXXXXX)
cp -a lifecycle "$copy/"
ASES_F3_EVIDENCE_COPY="$copy" python3 -S policy_test_portable.py
```

The separate syscall reproduction is `python3 -S -c "import ctypes,os; l=ctypes.CDLL(None,use_errno=True); print('landlock ABI:',l.syscall(444,None,0,1),'errno:',ctypes.get_errno()); print('kernel:',os.uname().release)"`. It changes no host policy. The syscall number is the probe's Linux-specific assumption, and its result is host-dependent.

`SHA256SUMS` hashes every regular artifact in this evidence directory except itself. The `lifecycle/l4/lab/alias-x` symlink targets `source/candidate-x.bin`; it is not represented as a regular-file digest. The fixed implementation under review remains unchanged.
