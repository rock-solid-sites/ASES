//! Small *synthetic* authority model for testing property-testing engines.
 //! This is not a Kernel-0 implementation or specification.
 //! Source obligation: docs/research/kernel-0/Kernel-0-Evidence-Packet.md
 //! Stale/superseded execution must not mutate current authoritative state.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Mutation {
    Baseline,
    AcceptAnyOldLease,
    ActorIdentityOnly,
    PartialSideEffect,
}

impl Mutation {
    pub fn from_environment() -> Self {
        match std::env::var("ASES_MUTANT").unwrap_or_else(|_| "baseline".into()).as_str() {
            "baseline" => Self::Baseline,
            "accept-any" => Self::AcceptAnyOldLease,
            "actor-only" => Self::ActorIdentityOnly,
            "partial-side-effect" => Self::PartialSideEffect,
            unexpected => panic!("unknown ASES_MUTANT={unexpected}"),
        }
    }
}

#[derive(Debug)]
struct Candidate {
    epoch: u64,
    actor: u8,
    writes: u64,
}

impl Candidate {
    fn new() -> Self {
        Self { epoch: 0, actor: 0, writes: 0 }
    }

    // 0: replace current execution, same actor; 1: replace with actor 1;
    // 2: original execution attempts a write; 3: current execution writes.
    fn apply(&mut self, step: u8, mutation: Mutation) -> bool {
        match step {
            0 => { self.epoch += 1; true }
            1 => { self.epoch += 1; self.actor = 1; true }
            2 => {
                let permitted = match mutation {
                    Mutation::Baseline | Mutation::PartialSideEffect => self.epoch == 0,
                    Mutation::AcceptAnyOldLease => true,
                    Mutation::ActorIdentityOnly => self.actor == 0,
                };
                if permitted || (mutation == Mutation::PartialSideEffect && self.epoch > 0) {
                    self.writes += 1;
                }
                permitted
            }
            3 => { self.writes += 1; true }
            _ => panic!("generator emitted invalid operation {step}"),
        }
    }
}

/// Returns the earliest model/implementation disagreement.
/// The oracle is a separate, intentionally simple transition calculation.
/// This checks the synthetic witness only, not any deployed kernel.
pub fn check_trace(steps: &[u8], mutation: Mutation) -> Result<(), String> {
    let mut expected_epoch: u64 = 0;
    let mut expected_writes: u64 = 0;
    let mut candidate = Candidate::new();

    for (position, &step) in steps.iter().enumerate() {
        let expected_permitted = match step {
            0 | 1 => { expected_epoch += 1; true }
            2 if expected_epoch == 0 => { expected_writes += 1; true }
            2 => false,
            3 => { expected_writes += 1; true }
            _ => return Err(format!("invalid test operation {step} at step {position}")),
        };
        let observed_permitted = candidate.apply(step, mutation);
        if expected_permitted != observed_permitted || expected_writes != candidate.writes {
            return Err(format!(
                "position={position} op={step} model_epoch={expected_epoch} \
                 expected_authorized={expected_permitted} actual_authorized={observed_permitted} \
                 expected_writes={expected_writes} actual_writes={}",
                candidate.writes
            ));
        }
    }
    Ok(())
}

#[cfg(test)]
mod controls {
    use super::*;
    #[test]
    fn compliant_and_violation_controls() {
        let witness = [0, 2]; // replacement then original execution attempts a stale write
        assert!(check_trace(&witness, Mutation::Baseline).is_ok());
        for mutation in [
            Mutation::AcceptAnyOldLease, Mutation::ActorIdentityOnly,
            Mutation::PartialSideEffect,
        ] {
            assert!(check_trace(&witness, mutation).is_err(), "{mutation:?} escaped control");
        }
        assert!(check_trace(&[2, 3, 0, 3, 1, 3], Mutation::Baseline).is_ok());
    }
}
