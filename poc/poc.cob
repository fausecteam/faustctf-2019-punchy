       IDENTIFICATION DIVISION.
       PROGRAM-ID. POC.
       PROCEDURE DIVISION.
       BEGIN.
       CALL "SYSTEM" USING FUNCTION
       LOWER-CASE("grep -air --after-context 1 flgbase32a data")
       STOP RUN.