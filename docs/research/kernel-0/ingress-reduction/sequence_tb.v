`timescale 1ns/1ps
module ingress_sequence_tb;
    parameter COUPLED=0, EXCLUSIVE=0;
    reg clk=0, reset;
    reg [4:0] lane_valid;
    reg [54:0] payloads;
    reg [21:0] expected, before_edge;
    reg wanted, wanted_resolved;
    wire [21:0] state;
    wire resolved, committed;
    fixed_ingress_machine #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) dut(
        clk,reset,lane_valid,payloads,state,resolved,committed);
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
                reset,lane_valid,payloads,expected,wanted_resolved,wanted);
            if (scanned!=6) $fatal(1,"invalid vector");
            #2;
            if (count>0 && state !== before_edge) $fatal(1,"premature publication");
            clk=1;
            #1;
            if (state !== expected || resolved !== wanted_resolved || committed !== wanted)
                $fatal(1,"case=%0d expected=%h/%b/%b actual=%h/%b/%b",
                    count,expected,wanted_resolved,wanted,state,resolved,committed);
            clk=0;
            count=count+1;
        end
        if (count==0) $fatal(1,"empty evidence");
        $display("PASS sequential cycles=%0d",count);
        $finish;
    end
endmodule
