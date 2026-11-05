module output_miter(input clk,reset,valid,input [14:0] proposal,output trigger,
    output [21:0] gold_state,gate_state,output gold_resolved,gate_resolved,gold_committed,gate_committed);
    gold a(clk,reset,valid,proposal,gold_state,gold_resolved,gold_committed);
    mutated_compact b(clk,reset,valid,proposal,gate_state,gate_resolved,gate_committed);
    assign trigger=(gold_state!=gate_state)||(gold_resolved!=gate_resolved)||(gold_committed!=gate_committed);
endmodule
