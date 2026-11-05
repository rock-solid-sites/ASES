module codec_contract(input wire [21:0] state_in, output wire bad);
    wire [17:0] encoded;
    wire [21:0] decoded;
    wire shape, code_valid;
    kernel0_encode enc(state_in,encoded,shape);
    kernel0_decode dec(encoded,decoded,code_valid);
    assign bad=shape && (!code_valid || decoded!=state_in);
endmodule

module step_contract(input wire [17:0] state_in, input wire [14:0] proposal, output wire bad);
    wire [21:0] original_in, original_next, decoded_next;
    wire valid_in, valid_next, original_commit, compact_commit;
    wire [17:0] compact_next;
    kernel0_decode initial_state(state_in,original_in,valid_in);
    kernel0_step original(original_in,proposal,original_next,original_commit);
    kernel0_compact_step compact(state_in,proposal,compact_next,compact_commit);
    kernel0_decode next_state(compact_next,decoded_next,valid_next);
    assign bad=valid_in && (!valid_next || original_next!=decoded_next || original_commit!=compact_commit);
endmodule
