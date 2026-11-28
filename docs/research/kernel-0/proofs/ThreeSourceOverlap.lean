import Lean

/-!
Joint report overlap for three normalized sources. Nonnegative region measures
are integer counts of disjoint units. Source identity and normalization are premises.
-/

namespace Kernel0.ThreeSourceOverlap

structure Atoms where
  onlyA : Nat
  onlyB : Nat
  onlyC : Nat
  onlyAB : Nat
  onlyAC : Nat
  onlyBC : Nat
  all : Nat

structure Reports where
  a : Nat
  b : Nat
  c : Nat
  ab : Nat
  ac : Nat
  bc : Nat

def AtomCounts (x : Atoms) : Reports where
  a := x.onlyA + x.onlyAB + x.onlyAC + x.all
  b := x.onlyB + x.onlyAB + x.onlyBC + x.all
  c := x.onlyC + x.onlyAC + x.onlyBC + x.all
  ab := x.onlyAB + x.all
  ac := x.onlyAC + x.all
  bc := x.onlyBC + x.all

def unionSize (x : Atoms) : Nat :=
  x.onlyA + x.onlyB + x.onlyC + x.onlyAB + x.onlyAC + x.onlyBC + x.all

def MinTriple (r : Reports) : Nat :=
  max (r.ab + r.ac - r.a) (max (r.ab + r.bc - r.b) (r.ac + r.bc - r.c))

def MaxTriple (r : Reports) : Nat :=
  min r.ab (min r.ac r.bc)

theorem feasible_triple_iff (r : Reports) (triple : Nat) :
    (∃ x, AtomCounts x = r ∧ x.all = triple) ↔
      MinTriple r ≤ triple ∧ triple ≤ MaxTriple r := by
  constructor
  · rintro ⟨x, rfl, rfl⟩
    unfold MinTriple MaxTriple AtomCounts
    simp only [Nat.max_le, Nat.le_min]
    omega
  · intro ⟨lower, upper⟩
    unfold MinTriple at lower
    unfold MaxTriple at upper
    simp only [Nat.max_le, Nat.le_min] at lower upper
    let x : Atoms := {
      onlyA := r.a + triple - (r.ab + r.ac)
      onlyB := r.b + triple - (r.ab + r.bc)
      onlyC := r.c + triple - (r.ac + r.bc)
      onlyAB := r.ab - triple
      onlyAC := r.ac - triple
      onlyBC := r.bc - triple
      all := triple
    }
    refine ⟨x, ?_, rfl⟩
    cases r
    simp only [AtomCounts, x, Reports.mk.injEq] at *
    omega

theorem inclusion_exclusion_without_truncated_subtraction (x : Atoms) :
    unionSize x + (AtomCounts x).ab + (AtomCounts x).ac + (AtomCounts x).bc =
      (AtomCounts x).a + (AtomCounts x).b + (AtomCounts x).c + x.all := by
  simp only [unionSize, AtomCounts]
  omega

def identicalReports : Reports := ⟨2, 2, 2, 1, 1, 1⟩

theorem equal_pairwise_reports_allow_distinct_union_sizes :
    ∃ small large, AtomCounts small = identicalReports ∧
      AtomCounts large = identicalReports ∧ unionSize small = 3 ∧ unionSize large = 4 :=
  ⟨⟨0, 0, 0, 1, 1, 1, 0⟩, ⟨1, 1, 1, 0, 0, 0, 1⟩, rfl, rfl, rfl, rfl⟩

theorem individually_plausible_counts_can_be_jointly_impossible :
    ¬ ∃ x, AtomCounts x = ⟨2, 2, 2, 2, 2, 0⟩ := by
  rintro ⟨x, matching⟩
  have possible := (feasible_triple_iff ⟨2, 2, 2, 2, 2, 0⟩ x.all).mp ⟨x, matching, rfl⟩
  change 2 ≤ x.all ∧ x.all ≤ 0 at possible
  omega

#print axioms feasible_triple_iff
#print axioms inclusion_exclusion_without_truncated_subtraction
#print axioms equal_pairwise_reports_allow_distinct_union_sizes
#print axioms individually_plausible_counts_can_be_jointly_impossible

end Kernel0.ThreeSourceOverlap
