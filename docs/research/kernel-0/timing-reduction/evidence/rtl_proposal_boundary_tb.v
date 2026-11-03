`timescale 1ns/1ps
module proposal_boundary_tb;
 reg clk=0,reset=0,valid=0; reg [14:0] proposal=0;
 wire [21:0] state; wire resolved,committed;
 reg [14:0] establish,grant,a,b,h; reg [21:0] pre,ea,eb,eh; integer fd,n,idx; reg [4095:0] path; reg bad; reg [21:0] expected,held;
 kernel0_machine dut(.clk(clk),.reset(reset),.valid(valid),.proposal(proposal),.state(state),.resolved(resolved),.committed(committed));
 task edge_step; begin #2; clk=1; #1; clk=0; #1; end endtask
 initial begin
  if (!$value$plusargs("vectors=%s",path)) $fatal(1,"missing vectors");
  bad=$test$plusargs("bad"); fd=$fopen(path,"r"); if(!fd) $fatal(1,"cannot open vectors");
  n=$fscanf(fd,"%h %h %h %h %h %h %h %h %h\n",establish,grant,a,b,h,pre,ea,eb,eh); if(n!=9) $fatal(1,"bad vectors");
  for(idx=0;idx<4;idx=idx+1) begin
   reset=1;valid=0;edge_step();reset=0;valid=1;proposal=establish;edge_step();proposal=grant;edge_step();
   if(state!==pre) $fatal(1,"setup case=%0d state=%h expected=%h",idx,state,pre);
   if(idx==1) proposal=b; else proposal=a;
   #2;
   if(idx==2) proposal=h;
   #2;
   case(idx) 0:expected=ea;1:expected=eb;2:expected=bad?ea:eh;3:expected=ea;endcase
   $display("case=%0d sampled=%h expected=%h",idx,proposal,expected);
   clk=1;#1;
   if(state!==expected || resolved!==1 || committed!==1) $fatal(1,"case=%0d state=%h expected=%h resolved=%b committed=%b",idx,state,expected,resolved,committed);
   held=state;clk=0;#1;
   if(idx==2) proposal=b;
   if(idx==3) begin proposal=h;#2;proposal=b;end
   #2;if(state!==held) $fatal(1,"postedge case=%0d changed state",idx);
  end
  $display("PASS four proposal boundary cases");$finish;
 end
endmodule
