# Clean-room review packet manifest

Target commit: `b49e1f66ddd91e501794f6c9381e1e96c19b096c`.

Each reviewer received a distinct `/tmp` snapshot containing only:
- `l1/l1.py`, `l3/l3.py`, `l4/l4.py`;
- `l5/l5_integrated.py`, `verify_l5_integrated.py`, the integrated raw JSON and three per-case L4 outputs;
- `l5_write.py`, `verify_l5_write.py`, baseline discriminator raw and baseline L4 raw;
- `Phase-I-Verification.md` at `511a5272e92155bd5ace7be2bb13fd2ed3730b23`;
- `Phase-I-Closure.md` at `8277b7f3b87347ef0c8438e1b7b73f08f37f9992`;
- implementation launch provenance and model-specific review prompt.

Neither snapshot included `INTEGRATED-RESULT.md`, `RESULT.md`, `OBSTRUCTION.md`, or prior review files. The successful GLM trace stayed in its GLM packet. The first MiMo attempt accessed the GLM packet and was aborted/excluded; the valid MiMo retry trace contains no references to another packet. The two successful review reports were not disclosed to one another.

The reviewer reports are independent model observations, not a vote. The coordinator synthesis resolves conflicting verdicts using the reviewed source/raw evidence and the verified source pins.
