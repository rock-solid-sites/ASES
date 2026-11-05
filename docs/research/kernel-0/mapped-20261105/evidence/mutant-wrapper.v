module mutated_compact(input clk,reset,valid,input [14:0] proposal,output [21:0] state,output resolved,committed);
    wire actual_committed;
    mapped_compact inner(clk,reset,valid,proposal,state,resolved,actual_committed);
    assign committed=actual_committed ^ valid;
endmodule
