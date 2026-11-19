#[path = "support/resource_properties.rs"]
mod resource_properties;
use proptest::prelude::*;
proptest! {
    #![proptest_config(ProptestConfig::with_cases(120))]
    #[test]
    fn actual_sqlite_admission_conserves_budget(steps in proptest::collection::vec(1u8..81u8, 0..20)) {
        let observed = resource_properties::verify_claim_sequence(&steps);
        prop_assert!(observed.is_ok(), "REAL_STORE_COUNTEREXAMPLE steps={steps:?}; result={observed:?}");
    }
}
