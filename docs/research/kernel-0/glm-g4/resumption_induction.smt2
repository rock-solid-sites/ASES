; Resumption induction for the repaired selector-rollback rule. One gate.
; State: d live decision counter, c live believed tenure, t gate floor,
; h gate binding (-1 when closed), ub a lineage-extending commit occurred,
; cl lineage tenure. Fixed restore parameters: d0 image horizon, m trace
; bound (floors plus issued summaries), ds true last decision, cs true
; selected tenure. The trace lemma and the spool lemma are asserted as
; premises inside `published', proved by the floor-monotonicity argument in
; the study: a binding is either current (cl) or forever shadowed by the
; floors that voted for later commits.
(set-logic QF_LIA)
(declare-const d Int)
(declare-const c Int)
(declare-const t Int)
(declare-const h Int)
(declare-const ub Bool)
(declare-const cl Int)
(declare-const d0 Int)
(declare-const m Int)
(declare-const ds Int)
(declare-const cs Int)
(declare-const q Int)
(declare-const r Int)
(declare-const b Int)
; Restore-time parameter facts: commits are traced (cs <= m), traces bound
; the pending attempt (m <= ds + 1), the image decided at most ds.
(define-fun params () Bool
  (and (<= 0 cs) (<= cs m) (<= m (+ ds 1)) (<= 0 d0) (<= 0 m) (<= d0 ds)))
(define-fun inv ((d Int) (c Int) (t Int) (h Int) (ub Bool) (cl Int)) Bool
  (and (<= 0 c) (<= c d) (<= cl d) (<= 0 t) (<= t (+ d 1))
       (<= d0 d) (<= m d) (<= cs cl)
       (or (= h (- 1)) (= h cl))          ; I1 an open gate holds the lineage
       (=> ub (= c cl))                   ; I2 unblocked implies coherent tenure
       (=> ub (< d0 t))))                 ; I3 unblocked floors pass the image
(define-fun freshq ((q Int)) Bool
  (or (> q m) (= q (+ ds 1))))
(define-fun published ((r Int) (b Int)) Bool
  (and (<= 0 r) (<= r d) (<= 0 b)
       (or (and (<= r d0) (<= b r) (=> (>= r cs) (= b cs)))
           (and (> r d0) (or (= b r) (= b c))))
       (or (< r t) (= b cl))))            ; spool/floor lemma premise
(assert params)
(push)
; Renumbered restore state satisfies the invariant.
(assert (and (<= d0 d) (<= m d) (or (= d d0) (= d m)) (<= 0 c) (<= c d0)
             (not ub) (= cl cs) (<= 0 t) (<= t m)
             (or (= h (- 1)) (= h cs))))
(assert (not (inv d c t h ub cl)))
(check-sat)
(pop)
(assert (inv d c t h ub cl))
(push)
; Prepare for the pending attempt above the floor closes the gate.
(assert (and (= q (+ d 1)) (> q t)))
(assert (not (inv d c q (- 1) ub cl)))
(check-sat)
(pop)
(push)
; A silent abort advances the counter without touching the gate.
(assert (= q (+ d 1)))
(assert (not (inv q c t h ub cl)))
(check-sat)
(pop)
(push)
; A commit with the gate closed at the attempt extends the lineage.
(assert (and (= q (+ d 1)) (= t q) (= h (- 1)) (freshq q)))
(assert (not (inv q q q (- 1) true q)))
(check-sat)
(pop)
(push)
; Delivering a published summary at or above the floor keeps the open gate
; on the lineage tenure.
(assert (and (published r b) (>= r t)))
(assert (not (inv d c r b ub cl)))
(check-sat)
(pop)
; Control: without withholding, a fresh pre-unblock abort publishes its
; stale remembered tenure and an open gate accepts it.
(push)
(assert (and (not ub) (= r (+ d 1)) (> r d0) (= b c) (< c cs)))
(assert (not (inv d c r b ub cl)))
(check-sat)
(pop)
; Control: without renumbering, a commit re-decides a settled traced
; attempt q2 (cs <= q2 <= m, not the true pending one); the gate's floor
; already sits at q2 from the old prepare, and the forged summary opens it
; on the re-decided tenure instead of the lineage.
(declare-const d2 Int)
(declare-const t2 Int)
(declare-const h2 Int)
(declare-const q2 Int)
(push)
(assert (and (<= cs q2) (<= q2 m) (<= q2 ds) (not (= q2 (+ ds 1)))
             (= d2 q2) (= t2 q2) (= h2 q2) (not (= h2 cs))))
(check-sat)
(pop)
