        
# Original code
        
        /* *************** INPUT PINS *********************/
        /*PIN   1  =   CLK       ;*/ /* externally connected to IO5 */ 
        PIN   2  =   i2          ; /*     D3                       */ 
        PIN   3  =   i3          ; /*     A17                      */ 
        PIN   4  =   i4          ; /*     Rd/not Write         */ 
        PIN   5  =   i5          ; /*     A18                      */ 
        PIN   6  =   i6          ; /*     A19                      */ 
        PIN   7  =   i7          ; /*     A20                      */ 
        PIN   8  =   i8          ; /*     not LDS                  */
        PIN   9  =   i9          ; /*     not MS                   */
        
        /* *************** OUTPUT PINS *********************/
        /* PIN   20 =   VCC          ; */    /*    */
        PIN   19 =   o19         ; /*     Not RAM                     */ 
        PIN   18 =   o18         ; /*     Not ROM                     */ 
        PIN   17 =   o17         ; /*     IO3                         */ 
        PIN   16 =   o16         ; /*     IO4                         */ 
        PIN   15 =   o15         ; /*     IO5                         */ 
        PIN   14 =   o14         ; /*     IO6                         */ 
        PIN   13 =   rf13        ; /*     Not connected               */ 
        PIN   12 =   o12         ; /*     IO8                         */ 
        PIN   11 =   !OE         ; /*     GND                         */
        
        /*CLK i2 i3 i4 i5 i6 i7 i8 i9 GND 
        /OE o12 rf13 o14 o15 o16 o17 o18 o19 VCC 
        */
        /*
        @ues 3030200000000000
        */
          /*equations */
        
        ! o19 = !i3 & !i5 & !i6 & i7 & !i8 & !i9 ;
        o19.oe = 'b' 1 ;
        
        ! o18 = !i7 & !i8  & !i9 ;
        o18.oe = 'b' 1 ;
        
        o17 = i3 & i4 & i5 & !i6 & i7 & !i8 & rf13 & !i9 ;
        o17.oe = 'b' 1 ;
        
        ! o16 = i4 & i5 & !i6 & i7 & !i8 & !i9 
            # i3 & i4 & !i5 & i6 & i7 & !i8 & !i9 ;
        o16.oe = 'b' 1;
        
        o15 = i3 & !i4 & i5 & !i6 & i7 & !i8 & !i9;
        o15.oe = 'b' 1 ;
        
        o14 = i3 & i4 & i5 & !i6 & i7 & !i8 & !rf13 & !i9
            # !i3 & i4 & i5 & !i6 & i7 & !i8 & !i9 ;
        o14.oe = 'b' 1 ;
        
        rf13.d = i2 ;   /* !registered output */
        /* rf13.oe = 'b' 1 ; */
        o12 = i4 & i9 ;
        o12.oe = 'b' 1 ;
        /* *   checksum of original C4AA3     */
        

# Modified

        /* *************** INPUT PINS *********************/
        /*PIN   1  =   CLK       ;*/ /* externally connected to IO5 */ 
        PIN   2  =   i2          ; /*     D3                       */ 
        PIN   3  =   i3          ; /*     A17                      */ 
        PIN   4  =   i4          ; /*     Rd/not Write         */ 
        PIN   5  =   i5          ; /*     A18                      */ 
        PIN   6  =   i6          ; /*     A19                      */ 
        PIN   7  =   i7          ; /*     A20                      */ 
        PIN   8  =   i8          ; /*     not LDS                  */
        PIN   9  =   i9          ; /*     not MS                   */
        
        /* *************** OUTPUT PINS *********************/
        /* PIN   20 =   VCC          ; */    /*    */
        PIN   19 =   o19         ; /*     Not RAM                     */ 
        PIN   18 =   o18         ; /*     Not ROM                     */ 
        PIN   17 =   o17         ; /*     IO3                         */ 
        PIN   16 =   o16         ; /*     IO4                         */ 
        PIN   15 =   o15         ; /*     IO5                         */ 
        PIN   14 =   o14         ; /*     IO6                         */ 
        PIN   13 =   rf13        ; /*     Not connected               */ 
        PIN   12 =   o12         ; /*     IO8                         */ 
        PIN   11 =   !OE         ; /*     GND                         */
        
        /*CLK i2 i3 i4 i5 i6 i7 i8 i9 GND 
        /OE o12 rf13 o14 o15 o16 o17 o18 o19 VCC 
        */
        /*
        @ues 3030200000000000
        */
          /*equations */
        
        // nRAMCS   = !( (!nLDS && !nMS) && (A[20:17] == 4'b1000) )
        //
        ! nRAMCS = !A17 & !A18 & !A19 & A20 & !nLDS & !nMS ;
        nRAMCS.oe = 'b' 1 ;
        
        // nROMCS   = (!nLDS && !nMS) && (A[20:17] == 1'b1xxx)
        //
        ! nROMCS = !A20 & !nLDS  & !nMS ;
        nROMCS.oe = 'b' 1 ;
        
        // Fake GPIB/UART emulator: return D3_D value
        // (!nLDS && !nMS) && A[20:17] == 4'b0100 && RnW && D3_D
        IO3_DATA = A17 & RnW & A18 & !A19 & A20 & !nLDS & D3_D & !nMS ;
        IO3_DATA.oe = 'b' 1 ;

        // ( (!nLDS && !nMS) && A[20:17] == 4'b0100 && RnW && !D3_D ) || 
           ( (!nLDS && !nMS) && A[20:17] == 4'b0101 && RnW)
        IO6_DATA = A17 & RnW & A18 & !A19 & A20 & !nLDS & !D3_D & !nMS
            # !A17 & RnW & A18 & !A19 & A20 & !nLDS & !nMS ;
        IO6_DATA.oe = 'b' 1 ;
        
        // Fake GPIB/UART drive data bus
        // IO4_CE = (!nLDS && !nMS) && RnW && ( A[20:17] == 4'b010x || A[20:17] = 4'b0010 ) 
        !IO4_CE = RnW & A18 & !A19 & A20 & !nLDS & !nMS 
            # A17 & RnW & !A18 & A19 & A20 & !nLDS & !nMS ;
        IO4_CE.oe = 'b' 1;
        
        // Condition to clock D3 -> write operation
        // IO5_CLK = (!nLDS && !nMS) && !RnW && A[20:17] == 4'b0100
        IO5_CLK = A17 & !RnW & A18 & !A19 & A20 & !nLDS & !nMS;
        IO5_CLK.oe = 'b' 1 ;
        
        
        D3_D.d = D3 ;   /* !registered output */
        /* D3_D.oe = 'b' 1 ; */

        // Drive data from module to CPU
        D_CE = RnW & nMS ;
        D_CE.oe = 'b' 1 ; /* *   checksum of original C4AA3     */
        
