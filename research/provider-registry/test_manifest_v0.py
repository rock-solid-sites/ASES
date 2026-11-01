"""Manifest contract tests: fail closed on invalid core, allow new semantics."""
import copy
import unittest
from manifest_v0 import validate, schedulable

def example():
    return {"schema_version":1,"provider_id":"example","revision":1,"state":"active",
            "products":[{"product_id":"opaque","kind":"other",
                         "capabilities":[{"type":"quantum_batch_execution",
                                          "parameters":{"max_qubits":100}}],
                         "meters":[{"meter_id":"work","unit":"qubit-seconds",
                                    "measurement":"custom","period":"custom"}],
                         "configurations":[{"configuration_id":"a","properties":{"qubits":100}}]}],
            "facts":[{"key":"account.remaining","value":None,"source":"provider_api",
                      "observed_at":"2026-11-01T10:00:00Z","status":"unknown"}],
            "relationships":[{"type":"consumes","from":"opaque","to":"other.product"}],
            "extensions":{"vendor:anything":{"shape":{"arbitrary":[1,2,3]}}}}

class ManifestContract(unittest.TestCase):
    def test_unknown_future_execution_type(self): self.assertTrue(validate(example()))
    def test_new_product_kind_is_generic(self):
        x=example();x["products"][0]["kind"]="other";self.assertTrue(validate(x))
    def test_disallow_unregistered_product_kind(self):
        x=example();x["products"][0]["kind"]="quantum";self.assertRaises(ValueError,validate,x)
    def test_missing_core(self):
        x=example();del x["provider_id"];self.assertRaises(ValueError,validate,x)
    def test_unknown_core_field(self):
        x=example();x["oops"]=1;self.assertRaises(ValueError,validate,x)
    def test_duplicate_products(self):
        x=example();x["products"].append(copy.deepcopy(x["products"][0]));self.assertRaises(ValueError,validate,x)
    def test_duplicate_meter(self):
        x=example();x["products"][0]["meters"]*=2;self.assertRaises(ValueError,validate,x)
    def test_duplicate_configuration(self):
        x=example();x["products"][0]["configurations"]*=2;self.assertRaises(ValueError,validate,x)
    def test_unknown_value_is_null(self):
        x=example();x["facts"][0]["value"]=100;self.assertRaises(ValueError,validate,x)
    def test_naive_timestamp_rejected(self):
        x=example();x["facts"][0]["observed_at"]="2026-11-01T10:00:00";self.assertRaises(ValueError,validate,x)
    def test_inferred_not_verified(self):
        x=example();x["facts"][0].update(source="inferred",status="verified",value=10);self.assertRaises(ValueError,validate,x)
    def test_bool_revision_rejected(self):
        x=example();x["revision"]=True;self.assertRaises(ValueError,validate,x)
    def test_nan_rejected(self):
        x=example();x["extensions"]["bad"]=float("nan");self.assertRaises(ValueError,validate,x)
    def test_invalid_meter_period(self):
        x=example();x["products"][0]["meters"][0]["period"]="whatever";self.assertRaises(ValueError,validate,x)
    def test_unknown_meter_supported_as_custom(self):
        x=example();x["products"][0]["meters"][0]["unit"]="new_unit";self.assertTrue(validate(x))
    def test_retired_not_schedulable(self):
        x=example();x["state"]="retired";self.assertFalse(schedulable(x))
    def test_active_schedulable(self): self.assertTrue(schedulable(example()))
    def test_nested_vendor_extension(self):
        x=example();x["products"][0]["extensions"]={"newvendor":{"arbitrary":True}}
        self.assertTrue(validate(x))
if __name__=="__main__":unittest.main()
