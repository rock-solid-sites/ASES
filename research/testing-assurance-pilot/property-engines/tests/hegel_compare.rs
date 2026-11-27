use ases_property_engines_pilot::{check_trace, Mutation};
use hegel::generators as gs;
use hegel::TestCase;

#[hegel::test(test_cases = 500)]
fn stale_execution_cannot_write(tc: TestCase) {
    let steps = tc.draw(gs::vecs(gs::integers::<u8>().min_value(0).max_value(3)).max_size(64));
    let result = check_trace(&steps, Mutation::from_environment());
    if result.is_err() {
        tc.note(&format!("COUNTEREXAMPLE: steps={steps:?}; result={result:?}"));
    }
    assert!(result.is_ok(), "COUNTEREXAMPLE: steps={steps:?}; result={result:?}");
}
