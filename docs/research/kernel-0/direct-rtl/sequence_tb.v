`timescale 1ns/1ps
module sequence_tb;
    parameter COUPLED=0, EXCLUSIVE=0;
    reg clk=0, reset, valid;
    reg [14:0] proposal;
    reg [21:0] expected, before_edge;
    reg wanted, wanted_resolved;
    wire [21:0] state;
    wire resolved, committed;
    kernel0_machine #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) dut(
        .clk(clk),.reset(reset),.valid(valid),.proposal(proposal),
        .state(state),.resolved(resolved),.committed(committed));
    integer fd, count, scanned;
    reg [4095:0] path;
    initial begin
        if (!$value$plusargs("vectors=%s",path)) $fatal(1,"missing vectors");
        fd=$fopen(path,"r");
        if (!fd) $fatal(1,"cannot open vectors");
        count=0;
        while (!$feof(fd)) begin
            before_edge=state;
            scanned=$fscanf(fd,"%h %h %h %h %h %h\n",
                           reset,valid,proposal,expected,wanted_resolved,wanted);
            if (scanned!=6) $fatal(1,"invalid sequence vector");
            #2;
            if (count>0 && state !== before_edge) $fatal(1,"state changed between edges");
            clk=1;
            #1;
            if (state !== expected || resolved !== wanted_resolved || committed !== wanted)
                $fatal(1,"sequence=%0d state=%h expected=%h outcome=%b/%b expected=%b/%b",
                       count,state,expected,resolved,committed,wanted_resolved,wanted);
            clk=0;
            count=count+1;
        end
        if (count==0) $fatal(1,"empty evidence");
        $display("PASS sequential cycles=%0d",count);
        $finish;
    end
endmodule
