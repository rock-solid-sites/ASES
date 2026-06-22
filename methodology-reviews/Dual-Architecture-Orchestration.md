# Agent Orchestration Strategy

This project utilizes a dual-architecture approach to AI agent orchestration. We combine **OpenCode** and **Crosslink** to maximize parallel development speed while preventing agents from interfering with each other's compilation and testing loops.

## The Two Architectures

### 1. Crosslink: The Asynchronous Factory Floor
**Architecture:** Isolated State (Git Worktrees & Distributed Locks)
**Use Case:** Parallel code writing and the "Builder" phase.

When multiple agents write code in a compiled language (Go), they cannot share a filesystem. If Agent A runs `go test ./...` while Agent B is writing a function, the tests will fail.

To solve this, we use `crosslink kickoff` and `crosslink swarm`. Crosslink launches background agents in hidden, isolated Git worktrees.
* **Benefits:** Complete isolation. Agent A and Agent B can write, compile, and test simultaneously without collisions.
* **When to use:** Use Crosslink to assign open issues to agents for heavy codebase modifications.

### 2. OpenCode: The Live Command Center
**Architecture:** Shared State (Active Terminal & Interactive REPL)
**Use Case:** Codebase exploration, API testing, debugging, and the "Adversarial/Verifier" phases.

OpenCode acts as the primary orchestrator and the ultimate tool for discovery and verification. 
* **Benefits:** It possesses highly optimized, purpose-built tools (`Glob`, `Grep`, `Read`) that safely search massive codebases without crashing context windows. Its interactive REPL allows for instant, iterative API testing and log parsing.
* **When to use:** Use OpenCode to coordinate the Crosslink agents, search the codebase, read logs, interactively debug API responses, and run rigorous Adversarial Reviews on the code produced by Crosslink Builders.

## The 3-Phase Workflow Execution

Every major feature in this project follows a strict 3-phase execution loop utilizing both tools:

1. **Builder Phase (Crosslink):** The OpenCode orchestrator uses the shell to run `crosslink kickoff <issue-id>`. A background agent spins up in an isolated worktree, drafts the code, writes tests, and commits the branch.
2. **Adversarial Review Phase (OpenCode):** Once the Builder branch is ready, it is checked out in the main terminal. A high-reasoning OpenCode agent performs rigorous edge-case attacks (SQL locking, XSS, LLM hallucinations, etc.) using its native search and bash tools.
3. **Verifier Phase (OpenCode):** A final OpenCode pass verifies the integration against the project specs and marks the Crosslink issue as resolved.
