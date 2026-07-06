// Testbench: ECRL inverter chain — switching activity & energy estimation
//
// Simulates a 4-stage ECRL inverter chain driven by a sinusoidal power-clock.
// Reports toggle counts and estimated energy savings vs. standard CMOS.

`timescale 1ns/1ps

module tb_ecrl;

    parameter real VDD     = 1.0;          // supply [V]
    parameter real C_LOAD  = 10e-15;       // load cap per stage [F]
    parameter real F_CLK   = 1e9;          // 1 GHz
    parameter real T_CLK   = 1.0 / F_CLK * 1e9;  // period [ns]
    parameter real Q_RES   = 1000.0;       // assumed resonator Q

    logic pck;
    logic in_t, in_f;
    logic [3:0] t_chain, f_chain;

    // Power-clock: modeled as 50% duty-cycle square wave
    // (In reality: sinusoidal at resonant frequency)
    initial pck = 0;
    always #(T_CLK/2) pck = ~pck;

    // Input stimulus
    initial begin
        in_t = 0; in_f = 1;
        repeat (5) @(posedge pck);
        forever begin
            in_t = $random & 1;
            in_f = ~in_t;
            @(posedge pck);
        end
    end

    // 4-stage ECRL inverter chain
    ecrl_inv dut0 (.pck(pck), .in_t(in_t),        .in_f(in_f),
                   .out_t(t_chain[0]), .out_f(f_chain[0]));
    ecrl_inv dut1 (.pck(pck), .in_t(t_chain[0]),  .in_f(f_chain[0]),
                   .out_t(t_chain[1]), .out_f(f_chain[1]));
    ecrl_inv dut2 (.pck(pck), .in_t(t_chain[1]),  .in_f(f_chain[1]),
                   .out_t(t_chain[2]), .out_f(f_chain[2]));
    ecrl_inv dut3 (.pck(pck), .in_t(t_chain[2]),  .in_f(f_chain[2]),
                   .out_t(t_chain[3]), .out_f(f_chain[3]));

    // Toggle counters
    int unsigned toggles [0:3];
    initial foreach (toggles[i]) toggles[i] = 0;
    always @(t_chain[0]) toggles[0]++;
    always @(t_chain[1]) toggles[1]++;
    always @(t_chain[2]) toggles[2]++;
    always @(t_chain[3]) toggles[3]++;

    int N_CYCLES = 1000;

    initial begin
        $dumpfile("tb_ecrl.vcd");
        $dumpvars(0, tb_ecrl);

        repeat (N_CYCLES) @(posedge pck);

        $display("\n=== ECRL Inverter Chain: Switching Activity ===");
        foreach (toggles[i])
            $display("  Stage %0d: %0d toggles  (activity = %.3f)",
                     i, toggles[i], real'(toggles[i]) / real'(N_CYCLES));

        // Energy estimate
        real E_cmos_total, E_pral_total;
        real alpha = real'(toggles[0] + toggles[1] + toggles[2] + toggles[3])
                     / (4.0 * N_CYCLES);
        E_cmos_total = 4 * alpha * 0.5 * C_LOAD * VDD * VDD * N_CYCLES;
        E_pral_total = 4 * alpha * (C_LOAD * VDD * VDD / Q_RES) * N_CYCLES;

        $display("\n=== Energy Estimate (%0d cycles) ===", N_CYCLES);
        $display("  Avg switching activity: %.3f", alpha);
        $display("  CMOS total energy:  %.4f fJ", E_cmos_total * 1e15);
        $display("  PRAL total energy (Q=%.0f): %.6f fJ", Q_RES, E_pral_total * 1e15);
        $display("  Savings:            %.2f%%", (1.0 - E_pral_total/E_cmos_total)*100);

        $finish;
    end

endmodule
