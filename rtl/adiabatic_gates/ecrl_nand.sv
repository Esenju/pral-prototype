// ECRL NAND2 — behavioral dual-rail model
//
// NAND truth table (dual-rail):
//   out_t = ~(a_t & b_t)  = a_f | b_f
//   out_f =  (a_t & b_t)

module ecrl_nand2 (
    input  logic pck,
    input  logic a_t, a_f,
    input  logic b_t, b_f,
    output logic out_t, out_f
);
    always_comb begin
        if (pck) begin
            out_t = a_f | b_f;
            out_f = a_t & b_t;
        end else begin
            out_t = 1'b0;
            out_f = 1'b0;
        end
    end
endmodule
