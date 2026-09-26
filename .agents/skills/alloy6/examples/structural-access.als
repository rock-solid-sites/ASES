module structural_access

abstract sig Principal {}
sig Human extends Principal {}
one sig Service extends Principal {}

sig Document {
  owner: one Principal,
  readers: set Principal
}

fact OwnersCanRead {
  all d: Document | d.owner in d.readers
}

pred shared[d: Document] {
  some d.readers - d.owner
}

run NontrivialSharing {
  some d: Document | shared[d]
} for 5 but exactly 3 Principal, exactly 2 Document expect 1

assert EveryDocumentHasReader {
  all d: Document | some d.readers
}

check EveryDocumentHasReader
  for 5 but exactly 3 Principal, exactly 2 Document expect 0

assert EveryReaderIsOwner {
  all d: Document | d.readers in d.owner
}

check EveryReaderIsOwner
  for 5 but exactly 3 Principal, exactly 2 Document expect 1
