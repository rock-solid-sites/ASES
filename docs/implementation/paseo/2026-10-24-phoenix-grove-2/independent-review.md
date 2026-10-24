# Independent review: Phoenix Grove 2 Codex provider

## Verification outcome

The updated evidence supports the provider installation and native use for all three listed models when reasoning is set to Off (`none`). DeepSeek and GLM each completed a real `exec_command` marker read and returned `PGS2_NATIVE_OK`. MiMo completed a no-tool text turn (`PGS2_MIMO_NONE_OK`), then a native `exec_command` marker read and final response (`PGS2_NATIVE_OK`) with reasoning Off. The MiMo tool turn took 85.539 seconds. Its earlier low-reasoning tool call completed but did not produce final text; the provider description now documents that limitation and exposes Off as its only reasoning option.

The direct Responses function-call/result probes also passed for DeepSeek, MiMo, and GLM. The Paseo catalog reports `codex-pgs2` as available. These checks establish model and protocol behavior in the recorded runs; they do not test selecting the provider from the Paseo interface.

## Credentials, routing, and preservation

The Paseo provider uses a non-secret `OPENAI_API_KEY` sentinel. Its launcher reads the key from the protected file, checks the `.secrets` directory and key file ownership and permissions, rejects symlinks, bounds and validates the key, then sets the Phoenix Grove base URL and launches the pinned Codex binary. It sets a dedicated `CODEX_HOME`; that home has a mode-0600 config setting `model_reasoning_effort = "none"`. The dedicated home and credential file keep this route separate from native Codex authentication. The recorded evidence says the key is absent from provider configuration and evidence files; the key is supplied to the child Codex process through its environment for authentication.

Fourteen watched pre-existing files have unchanged hashes and modes. The only Paseo config delta is `agents.providers.codex-pgs2`; the separate dedicated Codex config is an intentional addition. The Paseo service main PID stayed the same and its restart count remained zero. No Windows desktop files were written. The Windows desktop OpenCode config was inaccessible to read, so this review makes no claim about subscription 1's desktop configuration.

## Runtime and cleanup

Across the final native snapshots, dedicated process RSS ranged from 147,304 to 148,680 KiB (about 144–145 MiB), and HWM ranged from 147,676 to 150,224 KiB (about 144–147 MiB). All six disposable agents are recorded as archived across the two phases, and the after-archive process snapshot contains no dedicated PGS2 process. The Paseo service stayed active without a restart.

Native per-turn token records reconcile with their session totals: DeepSeek 16,245 input + 49 output = 16,294 total; GLM 15,537 + 31 = 15,568; MiMo across two turns 23,714 + 102 = 23,816. Cached input is included in input details, not an additional total; reasoning tokens are a detail of output. These are recorded session/per-turn usage values, not a claim about billing or a separate `LastUsage` field.

The saved native records show the selected model and resulting reasoning level, but do not record whether each model/reasoning setting was explicitly supplied or inherited from defaults. No Windows desktop configuration or UI selection was tested.
