yosys -p "logger -debug; read_verilog ram_design.v; synth_ecp5; write_json ram_design.json" -l ram_design.yosys.log
