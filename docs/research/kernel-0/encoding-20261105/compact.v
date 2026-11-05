// Experimental18-bit register encoding under frozen position0 exclusivity.
module kernel0_encode(input wire [21:0] wide, output wire [17:0] packed_state,
                      output wire valid_shape);
    wire [2:0] r0=wide[10:8], r1=wide[13:11], r2=wide[16:14];
    wire [4:0] code = (r0!=0) ? {2'b0,r0} :
                      (r1!=0) ? 5'd7+{2'b0,r1} :
                      (r2!=0) ? 5'd14+{2'b0,r2} : 5'd0;
    assign valid_shape = !((r0!=0 && r1!=0) || (r0!=0 && r2!=0) || (r1!=0 && r2!=0));
    assign packed_state = {wide[21:20],wide[19:17],code,wide[7:0]};
endmodule

module kernel0_decode(input wire [17:0] packed_state, output wire [21:0] wide,
                      output wire valid_code);
    wire [4:0] code=packed_state[12:8];
    wire [2:0] r0=(code>=1 && code<=7) ? code : 3'd0;
    wire [2:0] r1=(code>=8 && code<=14) ? code-5'd7 : 3'd0;
    wire [2:0] r2=(code>=15 && code<=21) ? code-5'd14 : 3'd0;
    assign valid_code=code<=21;
    // Invalid code is an invalid absent word, and the step holds/refuses it.
    assign wide=valid_code ? {packed_state[17:16],packed_state[15:13],r2,r1,r0,packed_state[7:0]}
                           : 22'h000002;
endmodule

module kernel0_compact_step #(parameter COUPLED=0, EXCLUSIVE=0)(
    input wire [17:0] state_in, input wire [14:0] proposal,
    output wire [17:0] state_out, output wire commit
);
    wire [21:0] wide, successor;
    wire valid_code, valid_shape, accepted;
    wire [17:0] encoded;
    kernel0_decode dec(state_in,wide,valid_code);
    kernel0_step #(.COUPLED(COUPLED),.EXCLUSIVE(EXCLUSIVE)) original(wide,proposal,successor,accepted);
    kernel0_encode enc(successor,encoded,valid_shape);
    assign state_out=(valid_code && valid_shape) ? encoded : state_in;
    assign commit=valid_code && valid_shape && accepted;
endmodule

module kernel0_compact_machine #(parameter COUPLED=0, EXCLUSIVE=0)(
    input wire clk, reset, valid, input wire [14:0] proposal,
    output wire [21:0] state, output reg resolved, committed
);
    reg [17:0] compact_state;
    wire [17:0] successor;
    wire accepted, code_valid;
    kernel0_compact_step #(.COUPLED(COUPLED),.EXCLUSIVE(EXCLUSIVE)) step(compact_state,proposal,successor,accepted);
    kernel0_decode observe(compact_state,state,code_valid);
    always @(posedge clk) begin
        if (reset) begin compact_state<=0; resolved<=0; committed<=0; end
        else begin
            resolved<=valid;
            committed<=valid && accepted;
            if (valid) compact_state<=successor;
        end
    end
endmodule
