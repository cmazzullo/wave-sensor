      SUBROUTINE DATTIM(IALF)
C
C
C        CURRENT DATE AND TIME RETURNED IN CHARACTER ARRAY TO
C        BE PRINTED IN 15A1 FORMAT IN THE FORM:
C               MO-DY-YR  HR:MN
C
C
      CHARACTER*15 IALF
      CHARACTER*8 HOURS
      CALL TIME(HOURS)
      CALL IDATE(IMO,IDY,IYR)
      WRITE(IALF,10)IMO,IDY,IYR,HOURS
   10 FORMAT(I2.2,'-',I2.2,'-',I2.2,2X,A5)
C
      RETURN
      END