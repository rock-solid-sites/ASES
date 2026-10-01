// Fixed bounded Kernel-0 transition law. See ../Kernel-0-Direct-RTL-Result.md.
// Profile parameters are elaboration constants, never runtime programs.
module kernel0_step #(
    parameter COUPLED = 0, parameter EXCLUSIVE = 0
)(
    input wire [21:0] state_in,
    input wire [14:0] proposal,
    output reg [21:0] state_out,
    output reg commit
);
    localparam ESTABLISH=0, GRANT=1, RESTRICT=2, REPLACE=3, DELEGATE=4,
               SET=5, FLIP=6, ACCEPT=7, RESUME=8, PAIR=9, MIXED=10;
    wire [3:0] op = proposal[3:0];
    wire [2:0] actor = proposal[6:4]; // 4 = trusted management observation
    wire [1:0] target = proposal[8:7];
    wire [2:0] value = proposal[11:9];
    wire [1:0] other = proposal[13:12];
    wire authentic = proposal[14]; // trusted ingress premise, NOT caller authority
    reg [21:0] proposed;
    reg admitted, wellformed;
    reg [2:0] current_rights, actor_rights, needed;

    function valid_state;
        input [21:0] s;
        reg [2:0] r0, r1, r2, r3, parent_rights;
        reg [1:0] parent;
        integer i;
        begin
            r0=s[10:8]; r1=s[13:11]; r2=s[16:14]; r3=s[19:17];
            parent=s[21:20];
            case (parent)
                1: parent_rights=r0;
                2: parent_rights=r1;
                3: parent_rights=r2;
                default: parent_rights=0;
            endcase
            valid_state=1;
            if (!s[0]) valid_state=(s == 0);
            else begin
                if (COUPLED && s[1] && s[2]) valid_state=0;
                if ((r0!=0 && r1!=0) || (r0!=0 && r2!=0) ||
                    (r1!=0 && r2!=0)) valid_state=0;
                if (EXCLUSIVE && r3!=0 && (r0!=0 || r1!=0 || r2!=0))
                    valid_state=0;
                for (i=0; i<4; i=i+1)
                    if (s[8+3*i +: 3]!=0 && !s[4+i]) valid_state=0;
                if (parent!=0 && (r3==0 || (r3 & ~parent_rights)!=0))
                    valid_state=0;
            end
        end
    endfunction

    always @* begin
        proposed=state_in;
        admitted=0;
        wellformed=0;
        needed=0;
        current_rights=state_in[8+3*target +: 3];
        actor_rights=0;
        if (actor<4) actor_rights=state_in[8+3*actor +: 3];
        // Exactly the 148 catalog templates, with either authenticity value.
        case (op)
            ESTABLISH: wellformed=(actor==4 && target==0 && value==0 && other==0);
            GRANT: wellformed=(actor==4 && value!=0 && other==0);
            RESTRICT: wellformed=(actor==4 && other==0);
            REPLACE: wellformed=(actor==4 && target<3 && other<3 &&
                                 target!=other && value==0);
            DELEGATE: wellformed=(actor<3 && target==3 && value!=0 && other==0);
            SET: wellformed=(actor<4 && target<2 && value<2 && other==0);
            FLIP: wellformed=(actor<4 && target<2 && value==0 && other==0);
            ACCEPT, RESUME: wellformed=(actor<4 && target==0 && value<2 && other==0);
            PAIR: wellformed=(actor<4 && target==0 && value<4 && other==0);
            MIXED: wellformed=(actor<4 && target==0 && value==0 && other==0);
            default: wellformed=0;
        endcase
        if (wellformed && authentic && valid_state(state_in)) begin
            if (op==ESTABLISH) begin
                if (!state_in[0]) begin
                    proposed[0]=1;
                    proposed[3]=0;
                    admitted=1;
                end
            end else if (state_in[0]) begin
                case (op)
                    GRANT: if (current_rights==0 && !state_in[4+target]) begin
                        proposed[8+3*target +: 3]=value;
                        proposed[4+target]=1;
                        if (target==3) proposed[21:20]=0;
                        admitted=1;
                    end
                    RESTRICT: if (current_rights!=0 && (value & ~current_rights)==0) begin
                        proposed[8+3*target +: 3]=value;
                        if (target==3 && value==0) proposed[21:20]=0;
                        if (target<3 && state_in[21:20]==({1'b0,target}+3'd1)) begin
                            proposed[19:17]=state_in[19:17] & value;
                            if (proposed[19:17]==0) proposed[21:20]=0;
                        end
                        admitted=1;
                    end
                    REPLACE: if (current_rights!=0 && !state_in[4+other] &&
                                 state_in[8+3*other +: 3]==0) begin
                        proposed[8+3*target +: 3]=0;
                        if (state_in[21:20]==({1'b0,target}+3'd1)) begin
                            proposed[19:17]=0;
                            proposed[21:20]=0;
                        end
                        proposed[8+3*other +: 3]=current_rights;
                        proposed[4+other]=1;
                        admitted=1;
                    end
                    DELEGATE: if (actor_rights!=0 && current_rights==0 &&
                                  !state_in[7] && (value & ~actor_rights)==0) begin
                        proposed[19:17]=value;
                        proposed[21:20]=actor[1:0]+2'd1;
                        proposed[7]=1;
                        admitted=1;
                    end
                    SET, FLIP, ACCEPT, RESUME, PAIR: begin
                        case (op)
                            SET, FLIP: needed=(3'b001 << target);
                            ACCEPT: needed=3'b100;
                            RESUME: needed=3'b001;
                            PAIR: needed=3'b011;
                        endcase
                        if ((needed & ~actor_rights)==0) begin
                            admitted=1;
                            case (op)
                                SET: proposed[1+target]=value[0];
                                FLIP: proposed[1+target]=~state_in[1+target];
                                ACCEPT: proposed[3]=value[0];
                                RESUME: begin
                                    if (value[0]!=state_in[3]) admitted=0;
                                    proposed[1]=value[0];
                                end
                                PAIR: proposed[2:1]=value[1:0];
                            endcase
                        end
                    end
                    default: admitted=0; // Including the entire mixed proposal.
                endcase
            end
        end
        commit=admitted && valid_state(proposed);
        state_out=commit ? proposed : state_in;
    end
endmodule

// Whole proposals are sampled at the rising edge; submission and resolution
// coincide. Reset is trusted initialization ONLY, outside the executor interface.
// Only state is authoritative. Combinational candidate signals are internal.
module kernel0_machine #(
    parameter COUPLED = 0, parameter EXCLUSIVE = 0
)(
    input wire clk, input wire reset, input wire valid,
    input wire [14:0] proposal,
    output reg [21:0] state,
    output reg resolved, output reg committed
);
    wire [21:0] successor;
    wire accept;
    kernel0_step #(.COUPLED(COUPLED), .EXCLUSIVE(EXCLUSIVE)) transition(
        .state_in(state), .proposal(proposal), .state_out(successor), .commit(accept));
    always @(posedge clk) begin
        if (reset) begin
            state<=0;
            resolved<=0;
            committed<=0;
        end else begin
            resolved<=valid;
            committed<=valid && accept;
            if (valid) state<=successor;
        end
    end
endmodule
