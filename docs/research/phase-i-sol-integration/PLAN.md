# Independent integration investigation — 2026-11-06

Experimental execution-engine evidence; no change to canonical claims or ASES policy.
Prepared after source inspection and before the deciding runtime experiments.

## Frozen target and sources

Base assurance branch: `7a264832e9d601dd4f9fc82bb9dfc2ed1aa7d620`.
Dedicated branch: `research/phase-i-sol-integration-20261106`.

| Component | Exact commit | Executed surface |
| --- | --- | --- |
| F1 C11 | `29ec3960c4c60dfb5d5f76d1c5dba7d2ea32d38a` | c11_service.py, inherited SQLite holder |
| F3 L5 | `51b34aface9340b7e6821b8c40dc62ca38da15e2` | original manager/commit and move-cuts worker |
| F3 L6 | `0f348fda050e67f3d9081a7fc22078eddc547a61` | store.py and race/race_store.py |
| F4 published cut | `26db6db361be986cdd168045f510f5567ee9df53` | cut_sink.py and inherited managed sink |
| F4 receipt extension | `9226cd4b8cd155a1d1b8e6b0495c0e1b99b941b9` | same sink, witness's real reply suppression |

Consulted the Kernel-0 Evidence Packet at the assurance base and testing/debugging
ontology proposal at `f8c700af1451f8545129aba466204867d344f12a`. The proposal is
experimental. Kernel assumptions constrain interpretations; implementation convenience
cannot redefine authority, work identity, or permitted partial authoritative mutation.

## Small implementation packet

Reuse all component transition code unchanged, as separate Python processes. A disposable
Python research harness is appropriate; it is not a maintained authority service.
Use SQLite FULL/DELETE and the original filesystem publication/HTTP code. Export exact
source trees using Git, record hashes, and retain processes, responses, bytes and SQL.
Do not import any original check.py or acceptance predicates as the oracle.

The adapter may initialize trusted fixtures, copy an actually F1-accepted byte string
into the existing L5 fixture, and submit that string to L6/F4. It must record this as
test-only import, **not native cross-component acceptance or source authentication**.
The pinned L5 move experiment itself uses a synthetic accepted-object fixture. Its
L4 native bootstrap invokes Landlock; this host's ABI probe returns ENOSYS (38).
Do not bypass confinement and claim to have tested it.

Proposed causal envelope: run namespace, logical unit C, content SHA256, complete F1
opaque observation bundle, and an explicit descendant D / F4 C/p route mapping.
Carry the same canonical serialized envelope through L5 metadata, L6 accepted file,
F4 payload and receipt's journal hash. This is adapter evidence, not a native typed
identity already supplied by the services. Check every field independently on readback.

State representation is PRIMARY for this bounded investigation: accepted pair,
imported protected object, descendant ceiling, inventory live/disposed, local effect,
published cut and receipt are distinct states. No new production machine is introduced.

## Discriminating questions and predictions

1. Can an F1 non-accept mutation replace the stored observations of unchanged accepted
   content after a holder is configured for a different future acceptance? Compare a
   read-only restart and same-observation mutation. If so, qualify the retention claim
   and identify the missing immutability/lifetime premise.
2. Does a moved read-only L5 descendant prevent an F4 effect carrying that exact identity?
   Compare a separately authorized L5 grant and an adapter that refuses the send.
   Native F4 has no L5-state input; a published disallowed effect would falsify the
   proposed composition implication, not its flat local-token claim.
3. Does L6 removal know about the still-live L5 object sharing the logical unit identity?
   Compare creator/remover under the original lock and detached-scan negative control.
   A local empty inventory cannot substantiate a global empty work unit.
4. Preserve actual F1 commit/kill before import and L6 file-fsync/kill before catalog
   commit. Determine which committed prefixes survive and whether recovery fabricates
   the missing suffix. Missing pipeline atomicity is not itself a local SQLite bug.
5. Preserve remote publication with lost receipt, rejection before publication, retries,
   stale F4 tokens and cold recovery. Do not infer no effect from a failed reply.
6. Challenge the prior refinement checker with a valid rejected request between durable
   events, as well as altered identity, receipt and journal controls. A skipped event
   sequence number may denote an unjournaled rejection rather than missing durable work.

Qualify an independent observer using valid neighbors and deliberately invalid controls.
Do not claim universal refinement, clean-room model-family review, native confinement,
power-loss durability, external witness nonrollback, or independent archival retention.

## Stop/completion condition

Stop expanding when one important cross-boundary counterexample is reproduced and the
smallest missing interface is identified. Preserve targeted local positive/negative
controls, exact sources, raw traces, limitations, transition mapping, claim disposition,
and prioritized obligations; commit/push and create a draft PR. Avoid ordinary CI,
storage provisioning, production changes, and broad framework development.
