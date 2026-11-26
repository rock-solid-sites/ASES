; One arbitrarily selected member of a fixed resource-owner set.
; e is the committed epoch, h the epoch last installed at this gate.
; v is the largest generation this member ever voted for (a ghost variable).
; busy is an initiated replacement, ack an owner-held receipt from this member.
(set-logic QF_LIA)
(declare-const e Int)
(declare-const h Int)
(declare-const v Int)
(declare-const frozen Bool)
(declare-const busy Bool)
(declare-const ack Bool)
(declare-const msg Int)
(declare-const origin Int)

(define-fun inv ((epoch Int) (held Int) (vote Int)
                 (closed Bool) (moving Bool) (received Bool)) Bool
  (and (>= held 0)
       (ite closed
            (and (= vote (+ held 1))
                 (or (and (= held epoch) moving) (= vote epoch)))
            (and (= held epoch) (= vote held)))
       (=> received (and moving closed (= held epoch)))))

(define-fun pre () Bool (inv e h v frozen busy ack))
; An authentic command may be replayed from any previously initiated
; generation. A commit notice may be replayed from any committed generation.
(define-fun prepare-message () Bool
  (and (> msg 0) (<= msg (ite busy (+ e 1) e))
       (not frozen) (= msg (+ h 1))))
(define-fun commit-message () Bool
  (and (> msg 0) (<= msg e) frozen (= msg (+ h 1))))
; Any old signed vote, including a duplicate, may reach the selector.
(define-fun authentic-vote () Bool (and (> msg 0) (<= msg v)))

; Each call below is the *entire* local successor. A step confined to
; another member stutters. Global commit projects all-member receipt to ack.
(define-fun preserves () Bool
  (and (=> (not busy) (inv e h v frozen true ack))                  ; begin
       (=> prepare-message (inv e h msg true busy ack))            ; freeze + vote
       (=> (and busy authentic-vote (= msg (+ e 1)))
           (inv e h v frozen busy true))                           ; record receipt
       (=> (and busy ack) (inv (+ e 1) h v frozen false false))    ; commit
       (=> commit-message (inv e msg v false busy ack))))          ; activate

; 1. Bad initial state, 2. non-inductive step, 3. wrong terminal decision.
(push 1)
(assert (not (inv 0 0 0 false false false)))
(check-sat)
(pop 1)
(push 1)
(assert (and pre (not preserves)))
(check-sat)
(pop 1)
(push 1)
(assert (and pre (not frozen) (distinct (= origin h) (= origin e))))
(check-sat)
(pop 1)

; 4. Drop this member from the commit condition.
(push 1)
(assert (and pre busy (not (inv (+ e 1) h v frozen false false))))
(check-sat)
(pop 1)
; 5. Keep the member but credit a genuine vote from a previous generation.
(push 1)
(assert (and pre busy authentic-vote (< msg (+ e 1))
             (not (inv e h v frozen busy true))))
(check-sat)
(pop 1)
(exit)
