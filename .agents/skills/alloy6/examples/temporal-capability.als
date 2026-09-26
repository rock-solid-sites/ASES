module temporal_capability

abstract sig User {}
one sig Alice, Eve extends User {}

abstract sig Credential {
  owner: one User
}

one sig AliceCredential extends Credential {} {
  owner = Alice
}

sig Token {
  boundTo: one User
}

sig Item {}

one sig Store {
  var loggedIn: set User,
  var valid: set Token,
  var purchased: User -> set Item
}

pred init {
  no Store.loggedIn
  no Store.valid
  no Store.purchased
}

pred login[u: User, c: Credential, t: Token] {
  c.owner = u
  t.boundTo = u
  u not in Store.loggedIn

  Store.loggedIn' = Store.loggedIn + u
  Store.valid' = Store.valid + t
  Store.purchased' = Store.purchased
}

pred buy[u: User, t: Token, i: Item] {
  u in Store.loggedIn
  t in Store.valid
  t.boundTo = u
  i not in u.(Store.purchased)

  Store.loggedIn' = Store.loggedIn
  Store.valid' = Store.valid
  Store.purchased' = Store.purchased + u->i
}

pred stutter {
  Store.loggedIn' = Store.loggedIn
  Store.valid' = Store.valid
  Store.purchased' = Store.purchased
}

pred next {
  (some u: User, c: Credential, t: Token | login[u, c, t]) or
  (some u: User, t: Token, i: Item | buy[u, t, i]) or
  stutter
}

pred traces {
  init
  always next
}

run AliceCanBuy {
  traces
  eventually some Alice.(Store.purchased)
} for 5 but exactly 2 User, exactly 2 Token, exactly 2 Item,
  6 steps expect 1

assert EveCannotBuy {
  traces implies always no Eve.(Store.purchased)
}

check EveCannotBuy
  for 5 but exactly 2 User, exactly 2 Token, exactly 2 Item,
  6 steps expect 0
