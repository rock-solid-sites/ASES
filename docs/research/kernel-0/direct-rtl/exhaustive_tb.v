`timescale 1ns/1ps
module exhaustive_tb;
    parameter COUPLED=0, EXCLUSIVE=0;
    reg [21:0] state_in, expected;
    reg [14:0] proposal;
    reg wanted;
    wire [21:0] state_out;
    wire commit;
    kernel0_step #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) dut(
        .state_in(state_in), .proposal(proposal), .state_out(state_out), .commit(commit));
    integer fd, count, scanned;
    reg [4095:0] path;
    initial begin
        if (!$value$plusargs("vectors=%s",path)) $fatal(1,"missing vectors");
        fd=$fopen(path,"r");
        if (!fd) $fatal(1,"cannot open vectors");
        count=0;
        while (!$feof(fd)) begin
            scanned=$fscanf(fd,"%h %h %h %h\n", state_in, proposal, expected, wanted);
            if (scanned!=4) $fatal(1,"invalid vector at %0d",count);
            #1;
            if (state_out !== expected || commit !== wanted)
                $fatal(1,"case=%0d state=%h proposal=%h expected=%h/%b actual=%h/%b",
                       count,state_in,proposal,expected,wanted,state_out,commit);
            count=count+1;
        end
        if (count==0) $fatal(1,"empty evidence");
        $display("PASS exhaustive vectors=%0d",count);
        $finish;
    end
endmodule
