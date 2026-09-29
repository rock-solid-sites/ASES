"""Finite architecture countermodels, not an EDASES implementation or benchmark.

Python standard library only. Prints deterministic JSON for the protocol record.
All cost units are invented and commensurate within a comparison only.
"""
import itertools
import json
import math


def cache_cost(n, hits, recompute, lookup, validate, fixed):
    return n * (lookup + validate) + (n - hits) * recompute + fixed


def sat(clauses):
    assignments = itertools.product((False, True), repeat=2)
    satisfied = [all(any(values[abs(lit) - 1] == (lit > 0) for lit in clause)
                     for clause in clauses) for values in assignments]
    return any(satisfied)


def main():
    out = {}
    out['reuse_cost'] = {
        'assumptions': 'N=100, H=80, R=10, L=1, fixed lifecycle cost=70; V charged per request',
        'recompute': 100 * 10,
        'reuse_V2': cache_cost(100, 80, 10, 1, 2, 70),
        'reuse_V9': cache_cost(100, 80, 10, 1, 9, 70),
    }
    # Only the final value is demanded. Changing that contract changes this comparison.
    out['burst_repair'] = {
        'assumptions': '100 updates; only final output demanded; R=10, mark=0.1, check=1',
        'eager': 100 * 10,
        'dirty_then_demand': 100 * 0.1 + 10 + 1,
    }
    # A token for an observed object says nothing about newly inserted objects.
    old_children = frozenset()
    new_children = frozenset({'child'})
    old_parent_content_token = new_parent_content_token = 'parent-content-v1'
    out['negative_domain'] = {
        'cached_no_children': not old_children,
        'included_record_tokens_unchanged': old_parent_content_token == new_parent_content_token,
        'current_no_children': not new_children,
        'domain_epoch_changed': 7 != 8,
    }
    # A valid input key does not establish that a result was correctly computed.
    x = 3
    out['cache_corruption'] = {
        'input_key_matches': True,
        'cached_y': 7,
        'required_y': 2 * x,
        'scoped_verifier_accepts': 7 == 2 * x,
        'after_cache_removal_recompute': 2 * x,
    }
    histories = ({'decision': 'accept', 'constraint': 'offline'},
                 {'decision': 'accept', 'constraint': 'online'})
    summary = lambda h: h['decision']
    out['context_collision'] = {
        'summaries_equal': summary(histories[0]) == summary(histories[1]),
        'required_future_answers_equal': histories[0]['constraint'] == histories[1]['constraint'],
    }
    base = [(1,), (-1,)]
    out['negative_proof_scope'] = {
        'base_satisfiable': sat(base),
        'strengthened_satisfiable': sat(base + [(2,)]),
        'relaxed_satisfiable': sat([(1,)]),
        'assignments_enumerated_per_formula': 4,
    }
    # A hypothetical work floor, not a measured or proven EDASES computation lower bound.
    out['cold_recovery'] = {
        'assumptions': '100 disjoint required jobs; >=10 work units each; capacity=8 work units/time',
        'aggregate_time_lower_bound_given_assumptions': 100 * 10 / 8,
        'equal_job_batch_schedule_time': math.ceil(100 / 8) * 10,
        'hypothetical_deadline': 50,
        'deadline_possible_given_assumptions': 100 * 10 / 8 <= 50,
    }
    out['cascade_cost'] = {
        'assumptions': 'direct=10, cheap=1, check=1, expensive after escalation=10; quality unmeasured',
        'direct': 10,
        'escalation_0_2': 1 + 1 + 0.2 * 10,
        'escalation_0_9': 1 + 1 + 0.9 * 10,
    }
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
