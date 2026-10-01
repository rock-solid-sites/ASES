`timescale 1ns/1ps
module ingress_exhaustive_tb;
    parameter COUPLED=0, EXCLUSIVE=0;
    reg [21:0] state_in, expected;
    reg [4:0] lane_valid;
    reg [54:0] payloads;
    reg wanted;
    wire [21:0] state_out;
    wire valid, commit;
    wire [14:0] proposal;
    fixed_ingress front(lane_valid,payloads,valid,proposal);
    kernel0_step #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) law(
        state_in,proposal,state_out,commit);
    integer fd, count, scanned;
    reg [4095:0] path;
    initial begin
        if (!$value$plusargs("vectors=%s",path)) $fatal(1,"missing vectors");
        fd=$fopen(path,"r");
        if (!fd) $fatal(1,"cannot open vectors");
        count=0;
        while (!$feof(fd)) begin
            scanned=$fscanf(fd,"%h %h %h %h %h\n",state_in,lane_valid,payloads,expected,wanted);
            if (scanned!=5) $fatal(1,"invalid vector %0d",count);
            #1;
            if (!valid || state_out !== expected || commit !== wanted)
                $fatal(1,"case=%0d state=%h lanes=%h payloads=%h expected=%h/%b actual=%h/%b valid=%b",
                    count,state_in,lane_valid,payloads,expected,wanted,state_out,commit,valid);
            count=count+1;
        end
        if (count==0) $fatal(1,"empty evidence");
        $display("PASS exhaustive vectors=%0d",count);
        $finish;
    end
endmodule
