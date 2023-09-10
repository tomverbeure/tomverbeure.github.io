// Verilog version of basic cells with timing arcs for sta command
`timescale 1ns/1ns

(* blackbox *)
module INV(
    input A,
    output Y);

    specify 
        (A => Y) = 1;
    endspecify
endmodule

(* blackbox *)
module BUF(
    input A,
    output Y);

    specify 
        (A => Y) = 1;
    endspecify
endmodule

(* blackbox *)
module AND2(
    input A,
    input B,
    output Y);

    specify 
        (A => Y) = 1;
        (B => Y) = 1;
    endspecify
endmodule

(* blackbox *)
module XOR2(
    input A,
    input B,
    output Y);

    specify 
        (A => Y) = 1;
        (B => Y) = 1;
    endspecify
endmodule

(* blackbox *)
module DFF(
    input D,
    input CK,
    output Q);

    specify 
        (posedge CK *> (Q : D)) = 1;
        $setup(D, posedge CK, 0);
    endspecify
endmodule


