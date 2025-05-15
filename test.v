module top #(
    parameter integer WIDTH = 8,  // Basic parameter
    localparam DEPTH = WIDTH + 2, /* Local param
                      with calculation */
    parameter CONFIG = 
        (WIDTH > 8) ? 4'b1010 : 4'b0001,  // Complex expression
    parameter ENDPARAM = 3
) (
    input [WIDTH-1:0] data,
    output [31:0]     addr,
    input             en
);
    localparam SPECIAL_CASE = 8'hFF;  // Module body param
endmodule