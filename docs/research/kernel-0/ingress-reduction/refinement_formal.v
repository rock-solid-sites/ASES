// Assurance only: a separate relational specification, not a second ingress
// implementation in the machine. All 60 input bits are unconstrained in SAT.
module ingress_spec(input [4:0] lane_valid, input [54:0] payloads,
                    output valid, output [14:0] proposal);
    assign valid=(lane_valid!=0) && ((lane_valid & (lane_valid-5'd1))==0);
    wire [14:0] q0={1'b1,payloads[10:4],3'd0,payloads[3:0]};
    wire [14:0] q1={1'b1,payloads[21:15],3'd1,payloads[14:11]};
    wire [14:0] q2={1'b1,payloads[32:26],3'd2,payloads[25:22]};
    wire [14:0] q3={1'b1,payloads[43:37],3'd3,payloads[36:33]};
    wire [14:0] q4={1'b1,payloads[54:48],3'd4,payloads[47:44]};
    assign proposal=valid ? (({15{lane_valid[0]}} & q0) |
                            ({15{lane_valid[1]}} & q1) |
                            ({15{lane_valid[2]}} & q2) |
                            ({15{lane_valid[3]}} & q3) |
                            ({15{lane_valid[4]}} & q4)) : 15'd0;
endmodule

module ingress_formal(input [4:0] lane_valid, input [54:0] payloads, output ok);
    wire actual_valid, expected_valid;
    wire [14:0] actual, expected;
    fixed_ingress dut(lane_valid,payloads,actual_valid,actual);
    ingress_spec spec(lane_valid,payloads,expected_valid,expected);
    assign ok=(actual_valid==expected_valid && actual==expected);
endmodule

// Boundary proof from arbitrary defined state. The expectation is computed from
// the unchanged transition law and independently specified input abstraction.
module ingress_boundary_formal #(
    parameter COUPLED=0, EXCLUSIVE=0
)(input clk, reset, input [4:0] lane_valid, input [54:0] payloads, output ok);
    wire [21:0] state, successor;
    wire resolved, committed, accept, valid;
    wire [14:0] proposal;
    reg [21:0] expected_state;
    reg expected_resolved, expected_committed;
    fixed_ingress_machine #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) dut(
        clk,reset,lane_valid,payloads,state,resolved,committed);
    ingress_spec spec(lane_valid,payloads,valid,proposal);
    kernel0_step #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) law(
        state,proposal,successor,accept);
    always @(posedge clk) begin
        expected_state <= reset ? 22'd0 : (valid ? successor : state);
        expected_resolved <= !reset && valid;
        expected_committed <= !reset && valid && accept;
    end
    assign ok=(state==expected_state && resolved==expected_resolved &&
               committed==expected_committed);
endmodule
