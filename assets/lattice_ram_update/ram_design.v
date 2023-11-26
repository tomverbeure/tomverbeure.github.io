

module my_ram #(parameter MEM_SIZE=512, MEM_WIDTH=8)
    (
        input                           clk, 
        input                           mem_wr, 
        input  [$clog2(MEM_SIZE)-1:0]   mem_addr,
        input  [MEM_WIDTH-1:0]          mem_wdata,
        output reg [MEM_WIDTH-1:0]      mem_rdata,
    );

    // $clog2 requires Verilog-2005 or later...
    localparam mem_addr_bits    = $clog2(MEM_SIZE);   

    reg [MEM_WIDTH-1:0] mem[0:MEM_SIZE-1];

    initial begin
        $readmemh("mem_init_file.hex", mem);
    end

    always @(posedge clk)
        if (mem_wr) begin
            mem[mem_addr]   <= mem_wdata;
            mem_rdata       <= mem_wdata;       // Some Intel FPGA RAMs require this...
        end
        else
            mem_rdata  <= mem[mem_addr];

endmodule
