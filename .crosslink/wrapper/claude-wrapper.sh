#!/bin/bash
# Wrapper to translate Anthropic 'claude' CLI args to 'opencode run'
# Fix-then-activate per audit #505 §3.1c / issue #517:
# - Previously dropped --allowedTools and --permission-mode (shift 2 no forward) — silent enforcement loss.
# - Now forwards --allowedTools via CROSSLINK_ALLOWED_TOOLS env + audit log; maps --permission-mode to --auto where appropriate.
# - Container mode (launch.rs:1023) bypasses this wrapper and enforces --allowedTools directly — this wrapper fix restores local auditability.
# WHY: Without this fix, local --container none launches claim tool restriction but drop it; container is the only enforced path.
# WHAT: Preserve allowedTools in env for guard + log provenance; permission-mode mapped to --auto for bypass cases.
# HOW CERTAIN: Proven via opencode run --help (no --allowedTools flag) — direct forwarding would error; env preservation is the safe fix.
# WHAT-NOT-TESTED: No live container launch with --allowedTools denial proven in this wrapper edit session (covered by live kickoff verify below).

OPENCODE="/home/claude-code/.local/bin/opencode"

ARGS=()
PROMPT=""
MODEL=""
AGENT=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)
            MODEL="$2"
            shift 2
            ;;
        --agent)
            AGENT="$2"
            shift 2
            ;; 
        --dangerously-skip-permissions)
            ARGS+=("--auto")
            echo "[wrapper] --dangerously-skip-permissions -> --auto" >&2
            shift
            ;; # Claude Code → OpenCode equivalent
        --permission-mode)
            # Fix: previously dropped silently (shift 2). Now map known bypass modes to --auto, log others.
            MODE="$2"
            case "$MODE" in
                bypassPermissions|acceptEdits|auto)
                    ARGS+=("--auto")
                    echo "[wrapper] --permission-mode $MODE mapped to --auto" >&2
                    ;;
                default|dontAsk|plan)
                    echo "[wrapper] --permission-mode $MODE (no --auto mapping, guard-enforced)" >&2
                    ;;
                *)
                    echo "[wrapper] --permission-mode $MODE (unknown, no mapping)" >&2
                    ;;
            esac
            # Preserve original for audit
            export CROSSLINK_PERMISSION_MODE="$MODE"
            shift 2
            ;; # Claude Code — mapped/logged, not dropped
        --allowedTools)
            # Fix: previously dropped silently (shift 2). Now preserve in env + log; opencode run has no --allowedTools flag.
            TOOLS="$2"
            export CROSSLINK_ALLOWED_TOOLS="$TOOLS"
            echo "[wrapper] --allowedTools forwarded to CROSSLINK_ALLOWED_TOOLS (len ${#TOOLS})" >&2
            # Also log first 200 chars for audit
            echo "[wrapper] --allowedTools preview: ${TOOLS:0:200}" >&2
            shift 2
            ;;
        --)
            shift
            PROMPT="$*"
            break
            ;;
        *)
            shift
            ;;
    esac
done

# STRICT MODEL ENFORCEMENT
if [[ -z "$MODEL" || "$MODEL" == "opus" || "$MODEL" == "sonnet" || "$MODEL" == "haiku" ]]; then
    echo "=========================================================================" >&2
    echo "FATAL ERROR: Implicit or default Anthropic models ('$MODEL') are DISABLED." >&2
    echo "You MUST specify an explicit OpenCode model with a provider prefix." >&2
    echo "Allowed providers: opencode, opencode-go, google-vertex, nvidia" >&2
    echo "Examples:" >&2
    echo "  --model opencode/laguna-s-2.1-free" >&2
    echo "  --model opencode-go/deepseek-v4-flash" >&2
    echo "  --model google-vertex/gemini-3.1-pro-preview" >&2
    echo "  --model nvidia/meta/llama-4-maverick-17b-128e-instruct" >&2
    echo "=========================================================================" >&2
    
    # Sleep slightly so tmux logs capture this before the pane closes
    sleep 5 
    exit 1
fi

# Memory scope: wrap background tmux sessions with systemd-run to prevent
# a single session's subagents from OOMing the box.
# Only applies inside tmux; interactive sessions are not capped.
# Requires: sudo loginctl enable-linger $(whoami)
MEMORY_SCOPE="${OPENCODE_MEMORY_SCOPE:-3G}"
# When running inside tmux (non-interactive kickoff agent), auto-approve permissions
if [[ -n "$TMUX" ]]; then
    ARGS+=("--auto")
fi
if [[ -n "$TMUX" ]] && command -v systemd-run &>/dev/null; then
    # Ensure user systemd env is available inside tmux
    export XDG_RUNTIME_DIR="/run/user/$(id -u)"
    AGENT_FLAG=""
    [[ -n "$AGENT" ]] && AGENT_FLAG="--agent $AGENT"
    # Expose the runtime agent type so the crosslink-guard plugin can apply
    # per-agent-type permission overrides (see crosslink-guard.ts).
    [[ -n "$AGENT" ]] && export CROSSLINK_AGENT_TYPE="$AGENT"
    # Also expose allowed tools for guard audit
    [[ -n "${CROSSLINK_ALLOWED_TOOLS:-}" ]] && export CROSSLINK_ALLOWED_TOOLS
    [[ -n "${CROSSLINK_PERMISSION_MODE:-}" ]] && export CROSSLINK_PERMISSION_MODE
    exec systemd-run --scope --user \
        -p "MemoryMax=${MEMORY_SCOPE}" \
        -p "MemoryHigh=$(( ${MEMORY_SCOPE%G} * 1024 - 512 ))M" \
        "$OPENCODE" run --model "$MODEL" $AGENT_FLAG "${ARGS[@]}" "$PROMPT"
else
    AGENT_FLAG=""
    [[ -n "$AGENT" ]] && AGENT_FLAG="--agent $AGENT"
    [[ -n "$AGENT" ]] && export CROSSLINK_AGENT_TYPE="$AGENT"
    [[ -n "${CROSSLINK_ALLOWED_TOOLS:-}" ]] && export CROSSLINK_ALLOWED_TOOLS
    [[ -n "${CROSSLINK_PERMISSION_MODE:-}" ]] && export CROSSLINK_PERMISSION_MODE
    exec "$OPENCODE" run --model "$MODEL" $AGENT_FLAG "${ARGS[@]}" "$PROMPT"
fi
