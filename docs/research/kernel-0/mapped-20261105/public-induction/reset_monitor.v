// Assurance only: product state remains arbitrary until a sampled trusted reset.
module reset_monitored_miter(
    input clk,reset,valid,input [14:0] proposal,
    output trigger,output reg armed=1'b0,output raw_trigger,
    output [21:0] gold_state,gate_state,
    output gold_resolved,gate_resolved,gold_committed,gate_committed
);
    output_miter compare(clk,reset,valid,proposal,raw_trigger,gold_state,gate_state,
                         gold_resolved,gate_resolved,gold_committed,gate_committed);
    always @(posedge clk) armed<=armed||reset;
    assign trigger=armed&&raw_trigger;
endmodule
