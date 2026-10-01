// Static lane binding: lane 0..3 -> a0..a3, lane 4 -> management.
// Each lane's 11 bits are {other[1:0], value[2:0], target[1:0], opcode[3:0]}.
// Access to other lanes, clock, reset and state is outside a caller's control.
// No authority label or authenticity verdict is accepted from payload data.
module fixed_ingress(
    input wire [4:0] lane_valid,
    input wire [54:0] payloads,
    output reg valid,
    output reg [14:0] proposal
);
    reg [10:0] payload;
    reg [2:0] actor;
    always @* begin
        valid=1;
        payload=0;
        actor=0;
        case (lane_valid)
            5'b00001: begin payload=payloads[10:0];  actor=0; end
            5'b00010: begin payload=payloads[21:11]; actor=1; end
            5'b00100: begin payload=payloads[32:22]; actor=2; end
            5'b01000: begin payload=payloads[43:33]; actor=3; end
            5'b10000: begin payload=payloads[54:44]; actor=4; end
            default: valid=0; // No unique submission: all requests remain unsubmitted.
        endcase
        proposal=valid ? {1'b1,payload[10:4],actor,payload[3:0]} : 15'd0;
    end
endmodule

// The complete trusted digital machine reuses the frozen baseline unchanged.
module fixed_ingress_machine #(
    parameter COUPLED=0, EXCLUSIVE=0
)(
    input wire clk, reset,
    input wire [4:0] lane_valid,
    input wire [54:0] payloads,
    output wire [21:0] state,
    output wire resolved, committed
);
    wire valid;
    wire [14:0] proposal;
    fixed_ingress ingress(.lane_valid(lane_valid), .payloads(payloads),
                          .valid(valid), .proposal(proposal));
    kernel0_machine #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) baseline(
        .clk(clk), .reset(reset), .valid(valid), .proposal(proposal),
        .state(state), .resolved(resolved), .committed(committed));
endmodule
