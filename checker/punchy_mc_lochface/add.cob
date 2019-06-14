       IDENTIFICATION DIVISION.
       PROGRAM-ID. {{name}}.
       DATA DIVISION. WORKING-STORAGE SECTION. 01 FOO.
       05 {{var1}} PIC 9(4) VALUE {{val1}}.
       05 {{var2}} PIC 9(4) VALUE {{val2}}.
       PROCEDURE DIVISION. BEGIN.
       ADD {{var1}} TO {{var2}}.
       DISPLAY {{var2}}. STOP RUN.