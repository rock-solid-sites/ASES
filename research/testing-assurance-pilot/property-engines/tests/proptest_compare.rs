use ases_property_engines_pilot::{check_trace, Mutation};
use proptest::prelude::*;

proptest! {
    #![proptest_config(ProptestConfig::with_cases(500))]
    #[test]
    fn stale_execution_cannot_write(steps in proptest::collection::vec(0u8..4u8, 0..64)) {
        let result = check_trace(&steps, Mutation::from_environment());
        prop_assert!(result.is_ok(), "COUNTEREXAMPLE: steps={steps:?}; result={result:?}");
    }
}
