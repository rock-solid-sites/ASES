// One-step correspondence of the register boundary for arbitrary initial state,
// reset/enable/request. Oracle equivalence of the combinational law is separate.
module boundary_formal #(
    parameter COUPLED=0, EXCLUSIVE=0
)(input clk, reset, valid, input [14:0] proposal, output ok);
    wire [21:0] state, successor;
    wire resolved, committed, accept;
    reg [21:0] expected_state;
    reg expected_resolved, expected_committed;
    kernel0_machine #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) dut(
        .clk(clk),.reset(reset),.valid(valid),.proposal(proposal),
        .state(state),.resolved(resolved),.committed(committed));
    kernel0_step #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) law(
        .state_in(state),.proposal(proposal),.state_out(successor),.commit(accept));
    always @(posedge clk) begin
        expected_state <= reset ? 22'd0 : (valid ? successor : state);
        expected_resolved <= !reset && valid;
        expected_committed <= !reset && valid && accept;
    end
    assign ok=(state==expected_state && resolved==expected_resolved &&
               committed==expected_committed);
endmodule
