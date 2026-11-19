#[path = "support/resource_properties.rs"]
mod resource_properties;
use hegel::generators as gs;
use hegel::TestCase;
#[hegel::test(test_cases = 120)]
fn actual_sqlite_admission_conserves_budget(tc: TestCase) {
    let steps = tc.draw(gs::vecs(gs::integers::<u8>().min_value(1).max_value(80)).max_size(20));
    let observed = resource_properties::verify_claim_sequence(&steps);
    if observed.is_err() { tc.note(&format!("REAL_STORE_COUNTEREXAMPLE steps={steps:?}; result={observed:?}")); }
    assert!(observed.is_ok(), "REAL_STORE_COUNTEREXAMPLE steps={steps:?}; result={observed:?}");
}
