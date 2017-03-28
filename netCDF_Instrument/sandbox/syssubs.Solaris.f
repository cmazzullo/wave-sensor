      SUBROUTINE DATTIM(IALF)
C
C        CURRENT DATE AND TIME RETURNED IN CHARACTER ARRAY TO
C        BE PRINTED IN 15A1 FORMAT IN THE FORM:
C               MO-DY-YR  HR:MN
C
      CHARACTER*15 IALF
C
C     + + + LOCAL VARIABLES + + +
      INTEGER systim(3), sysdat(3)
C
C     + + + EXTERNALS + + +
      EXTERNAL IDATE, ITIME
C
C     + + + INTRINSICS + + +
      INTEGER MOD
      INTRINSIC MOD
C
C     + + + EXTERNAL DEFINITIONS + + +
C     ITIME IS A SUN FORTRAN SUBROUTINE
C     IDATE IS A STANDARD SUNOS SUN SYSTEM SUBROUTINE
C     THE SUN VMS VERSION OF IDATE IS CALL IDATE(M,D,Y)
C
C     + + + END SPECIFICATIONS + + +
C
      CALL IDATE(sysdat)
      CALL ITIME(systim)
C
C     sysdat(1) = DAY OF MONTH
C     sysdat(2) = MONTH OF YEAR
C     sysdat(3) = YEAR
C
C     systim(1) = HOUR SINCE MIDNIGHT
C     systim(2) = MINUTE SINCE HOUR
C     systim(3) = SEC SINCE MINUTE
C
      WRITE(IALF,10) sysdat(2), sysdat(1), MOD(sysdat(3),100),
     &               systim(1), systim(2)
   10 FORMAT(2(I2.2,'-'),I2.2,I4.2,':',I2.2)
C
      RETURN
      END
