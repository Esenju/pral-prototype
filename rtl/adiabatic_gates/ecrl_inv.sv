// Efficient Charge Recovery Logic (ECRL) Inverter — behavioral model
//
// ECRL uses a dual-rail (differential) encoding and a sinusoidal power-clock (pck).
// The power-clock ramps up slowly, allowing charge to be redistributed rather than
// dumped to ground. At pck HIGH: output evaluates. At pck LOW: output resets,
// charge returns to pck supply rail (energy recovery).
//
// This is a BEHAVIORAL model for simulation / energy estimation only.
// Real ECRL requires analog-aware layout (cross-coupled PMOS feedback, pck routing).
//
// Signal conventions:
//   in_t / in_f : true/false dual-rail input
//   out_t / out_f: true/false dual-rail output
//   pck : power-clock (sinusoidal, drives PMOS sources)

module ecrl_inv (
    input  logic pck,      // power-clock (sinusoidal approximation via PWM)
    input  logic in_t,     // true input
    input  logic in_f,     // false input (complement)
    output logic out_t,    // true output  = ~in_t
    output logic out_f     // false output = ~in_f = in_t
);
    // Evaluate phase: pck rising — cross-coupled outputs latch
    // Reset phase:    pck falling — outputs return to pck (discharged adiabatically)
    always_comb begin
        if (pck) begin
            out_t = in_f;   // ECRL inversion: out_t follows in_f
            out_f = in_t;
        end else begin
            out_t = 1'b0;   // reset (in real circuit: node floats to pck rail)
            out_f = 1'b0;
        end
    end

`ifdef POWER_ANNOTATION
    // Toggle counting for energy estimation
    // E_switch = alpha * C * Vdd^2 per cycle  (alpha = switching activity)
    // With ECRL: E_switch ≈ E_cmos / Q  (Q from resonant pck)
    int unsigned toggle_count_t = 0;
    int unsigned toggle_count_f = 0;
    always @(out_t) toggle_count_t++;
    always @(out_f) toggle_count_f++;
`endif

endmodule