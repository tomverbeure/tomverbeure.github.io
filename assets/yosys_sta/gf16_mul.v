
module gf16_mul(
    input            clk,
    input      [3:0] poly_a,
    input      [3:0] poly_b,
    output reg [3:0] poly_out,
    output     [3:0] poly_out_comb
    );

    reg  [3:0] a;
    reg  [3:0] b;
    wire [3:0] r;

    always @(posedge clk) begin
        a <= poly_a;
        b <= poly_b;
    end

    wire m_1_1 = a[0];
    wire m_1_2 = (a[1] ^ a[3]);
    wire m_1_3 = (a[2] ^ a[3]);
    wire m_2_1 = a[3];
    wire m_2_2 = (m_1_1 ^ m_1_3);
    wire m_2_3 = (m_1_2 ^ m_1_3);
    wire m_3_1 = m_1_3;
    wire m_3_2 = (m_2_1 ^ m_2_3);
    wire m_3_3 = (m_2_2 ^ m_2_3);

    assign r[0] = (a[0] & b[0]) ^ (a[3] & b[1]) ^ (m_1_3 & b[2]) ^ (m_2_3 & b[3]);
    assign r[1] = (a[1] & b[0]) ^ (m_1_1 & b[1]) ^ (m_2_1 & b[2]) ^ (m_3_1 & b[3]);
    assign r[2] = (a[2] & b[0]) ^ (m_1_2 & b[1]) ^ (m_2_2 & b[2]) ^ (m_3_2 & b[3]);
    assign r[3] = ^{(a[3] & b[0]), (m_1_3 & b[1]), (m_2_3 & b[2]), (m_3_3 & b[3]) };

    always @(posedge clk) begin
        poly_out <= r;
    end

    assign poly_out_comb = r;

endmodule


