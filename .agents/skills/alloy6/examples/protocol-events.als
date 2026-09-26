module protocol/events

sig Node {}
sig Payload {}

one sig Network {
  var pending: Node -> Node -> Payload,
  var delivered: Node -> Payload
}

enum EventKind { SendEvent, DeliverEvent, IdleEvent }

pred init {
  no Network.pending
  no Network.delivered
}

pred send[from, to: Node, payload: Payload] {
  from != to
  from->to->payload not in Network.pending
  Network.pending' = Network.pending + from->to->payload
  Network.delivered' = Network.delivered
}

pred deliver[from, to: Node, payload: Payload] {
  from->to->payload in Network.pending
  Network.pending' = Network.pending - from->to->payload
  Network.delivered' = Network.delivered + to->payload
}

pred stutter {
  Network.pending' = Network.pending
  Network.delivered' = Network.delivered
}

fun sendBindings: Node -> Node -> Payload {
  { from, to: Node, payload: Payload | send[from, to, payload] }
}

fun deliverBindings: Node -> Node -> Payload {
  { from, to: Node, payload: Payload | deliver[from, to, payload] }
}

fun eventKinds: set EventKind {
  { event: EventKind |
    (event = SendEvent and some sendBindings) or
    (event = DeliverEvent and some deliverBindings) or
    (event = IdleEvent and stutter)
  }
}

pred next {
  (one sendBindings and no deliverBindings and not stutter) or
  (one deliverBindings and no sendBindings and not stutter) or
  (stutter and no sendBindings and no deliverBindings)
}

pred traces {
  init
  always next
}

assert ExactlyOneEventPerTransition {
  traces implies always one eventKinds
}

run SendThenDeliverThenIdle {
  traces
  some disj from, to: Node | some payload: Payload |
    (send[from, to, payload]; deliver[from, to, payload]; always stutter)
} for exactly 2 Node, exactly 1 Payload, 5 steps expect 1

check ExactlyOneEventPerTransition
  for exactly 2 Node, exactly 2 Payload, 6 steps expect 0
