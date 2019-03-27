program dtype
!script to solve the ionization/shock front equations for 
!the StarBench paper (Bisbas et al., 2015, MNRAS, 453, 1324)

implicit none
real :: t_start         !start time in Myr
real :: t_end           !end time in Myr
real :: Rst             !initial Stromgren radius
real :: h               !Runge-Kutta variable
real :: ci              !sound speed of ionized gas
real :: co              !sound speed of neutral gas
real :: R_IF            !position of ionization front
real :: t
real,allocatable::RIF(:),time(:),RSF(:),RIF2(:)
integer :: n,k            !steps
real :: fsb,f_sim

!RIF is Raga-I solution
!RIF2 is Raga-II solution
!f_sim is the StarBench solution **FOR THE LATE PHASE ONLY**

interface
function f(R_IF,Rst,ci,co)
real, intent(in) :: R_IF,Rst,ci,co
end function f
function f_spitzer(Rst,ci,t)   ! <<---- Spitzer solution
real,intent(in) :: Rst,ci,t
end function f_spitzer
function VIF(R_IF,Rst,ci,co)
real,intent(in) :: R_IF,Rst,ci,co
end function VIF
function f_SF(V_IF,co)
real,intent(in) :: V_IF,co
end function f_SF
function f_HI(Rst,ci,t)  ! <<------ Hosokawa-Inutsuka solution
real,intent(in) :: Rst,ci,t
end function f_HI
function VSF(V_SF,co)
real,intent(in) :: V_SF,co
end function VSF
function f_RagaII(R_IF,Rst,ci,co)
real,intent(in) :: R_IF,Rst,ci,co
end function f_RagaII

end interface

!!Raga's paper
!t_start=0.0
!t_end=0.15
!Rst=0.001465
!ci=10.0
!co=1.0

!Early phase (StarBench paper)
!t_start=0.0 !Myr
!t_end=0.141 !Myr
!Rst=0.314   !pc
!ci=12.85*1.0226903    !km/s
!co=0.288*1.0226903    !km/s for 10K medium
!!co=0.91*1.0226903     !km/s for 100K medium

!Late phase !StarBench paper)
!t_start=0.0     !Myr
!t_end=3.0     !Myr
!Rst=0.314       !pc
!ci=12.85*1.0226903         !km/s --> pc/Myr
!co=2.87*1.0226903        !km/s --> pc/Myr
!open(unit=3,file='output.dat',status='replace')

!Sprai late phase
t_start=0.0             !Myr
t_end=3.0               !Myr
Rst=0.326778            !pc
ci=15.5287*1.0226903    !km/s --> pc/Myr
co=3.72092*1.0226903    !km/s --> pc/Myr
open(unit=3,file='output2.dat',status='replace')

write(3,*) '# 1:step, 2:time, 3:Spitzer, 4:Hosokawa-Inutsuka, 5:Raga-I, 6:Raga-II, 7:StarBench'

n=5000 !steps

allocate(RIF(0:n),time(0:n),RSF(0:n),RIF2(0:n))

h=(t_end-t_start)/real(n)

call rk4(f,t_start,Rst,ci,co,h,n,RIF,time) ! <<----- Raga-I solution
call rk4_b(f_SF,Rst,VIF,ci,co,h,n,RIF,RSF)
call rk4_c(f_RagaII,t_start,Rst,ci,co,h,n,RIF2) ! <<----- Raga-II solution
do k=0,n
  fsb=1.-0.732734*exp(-time(k))
  f_sim=RIF2(k)+fsb*(RIF(k)-RIF2(k))
  write(3,'(I6,200E15.7)') k,time(k),f_spitzer(Rst,ci,time(k)),f_HI(Rst,ci,time(k)),&
 &RIF(k),RIF2(k),f_sim
enddo

end program dtype

  function f(R_IF,Rst,ci,co)
  implicit none
  real :: f
  real, intent(in) :: R_IF,Rst,ci,co

  f = Rst**(3./4.)*ci*R_IF**(-3./4.) - (co*co/ci/Rst**(3./4.))*R_IF**(3./4.)
  end function f

  function f_spitzer(Rst,ci,t)
  implicit none
  real :: f_spitzer
  real, intent(in) :: Rst,ci,t

  f_spitzer = Rst*(1.+(7./4.)*ci*t/Rst)**(4./7.)
  end function f_spitzer

  function f_HI(Rst,ci,t)
  implicit none
  real :: f_HI
  real, intent(in) :: Rst,ci,t

  f_HI = Rst*(1.+(7./4.)*(sqrt(4./3.))*ci*t/Rst)**(4./7.)
  end function f_HI

  function VSF(V_SF,co)
  implicit none
  real :: VSF
  real, intent(in) :: V_SF,co

  VSF = 0.5*(V_SF + sqrt(V_SF**2 + 4*co**2))
  end function VSF

  function VIF(R_IF,Rst,ci,co)
  implicit none
  real :: VIF
  real, intent(in) :: R_IF,Rst,ci,co

  VIF = Rst**(3./4.)*ci*R_IF**(-3./4.) - (co*co/ci/Rst**(3./4.))*R_IF**(3./4.)
  end function VIF

  function f_SF(V_IF,co)
  implicit none
  real :: f_SF
  real, intent(in) :: V_IF,co

  f_SF = 0.5*(V_IF + sqrt(V_IF**2 + 4*co**2))
  end function f_SF

  function f_RagaII(R_IF,Rst,ci,co)
  implicit none
  real :: f_RagaII
  real, intent(in) :: R_IF,Rst,ci,co
  
  !f_RagaII = sqrt((4./3.)*ci**2*Rst**(3./2.)*R_IF**(-3./2.)-6.*(co**2)*log(R_IF))
  f_RagaII = sqrt(abs((4./3.)*ci**2*Rst**(3./2.)*R_IF**(-3./2.)-(co**2)/2.))
  if ((4./3.)*ci**2*Rst**(3./2.)*R_IF**(-3./2.)-(co**2)/2.<0) f_RagaII=0.0
!  write(6,*) R_IF, log(R_IF), (4./3.)*Rst**(3./2.)*R_IF**(-3./2.)-6.*(co**2/ci)*log(R_IF)
  end function f_RagaII

subroutine rk4(f,t_start,Rst,ci,co,h,n,RIF,time) ! Raga-I solution
  implicit none
  real :: f1,f2,f3,f4,ta
  real :: R_IF,t
  real,intent(in) :: h,Rst,ci,co,t_start
  integer,intent(in) :: n
  real,intent(out) :: RIF(0:n),time(0:n)
  integer :: k
  interface
  function f(R_IF,Rst,ci,co)
  real, intent(in) :: R_IF,Rst,ci,co
  end function f
  end interface
  ta = t_start
  R_IF=Rst
  time(0)=ta
  RIF(0)=Rst
  do k=1,n
      f1 = h*f(R_IF,Rst,ci,co)       
      f2 = h*f(R_IF + 0.5*f1,Rst,ci,co)   
      f3 = h*f(R_IF + 0.5*f2,Rst,ci,co)   
      f4 = h*f(R_IF + f3,Rst,ci,co)
      t = ta + h*real(k) 
      R_IF = R_IF + (f1 + 2*f2  +2*f3 + f4)/6.0
      RIF(k)=R_IF
      time(k)=t
  enddo
end subroutine rk4

subroutine rk4_b(f_SF,Rst,VIF,ci,co,h,n,RIF,RSF) ! Shock front solution
  implicit none
  real :: f1,f2,f3,f4
  real :: R_SF,V_IF
  real,intent(in) :: h,ci,co,Rst,RIF(0:n)
  integer,intent(in) :: n
  real,intent(out) :: RSF(0:n)
  integer :: k
  interface
  function f_SF(V_IF,co)
  real, intent(in) :: V_IF,co
  end function f_SF
  function VIF(R_IF,Rst,ci,co)
  real,intent(in) :: R_IF,Rst,ci,co
  end function VIF
  end interface
  RSF(0)=Rst
  R_SF=Rst
  do k=1,n
      V_IF = VIF(RIF(k),Rst,ci,co)
      f1 = h*f_SF(V_IF,co)       
      f2 = h*f_SF(V_IF + 0.5*f1,co)   
      f3 = h*f_SF(V_IF + 0.5*f2,co)   
      f4 = h*f_SF(V_IF + f3,co)
      R_SF = R_SF + (f1 + 2*f2  +2*f3 + f4)/6.0
      RSF(k)=R_SF
  enddo
end subroutine rk4_b

subroutine rk4_c(f_RagaII,t_start,Rst,ci,co,h,n,RIF2) ! Raga-II solution
  implicit none
  real :: f1,f2,f3,f4,ta
  real :: R_IF,t
  real,intent(in) :: h,Rst,ci,co,t_start
  integer,intent(in) :: n
  real,intent(out) :: RIF2(0:n)
  integer :: k
  interface
  function f_RagaII(R_IF,Rst,ci,co)
  real, intent(in) :: R_IF,Rst,ci,co
  end function f_RagaII
  end interface
  ta = t_start
  R_IF=Rst
  RIF2(0)=Rst
  do k=1,n
      f1 = h*f_RagaII(R_IF,Rst,ci,co)       
      f2 = h*f_RagaII(R_IF + 0.5*f1,Rst,ci,co)   
      f3 = h*f_RagaII(R_IF + 0.5*f2,Rst,ci,co)   
      f4 = h*f_RagaII(R_IF + f3,Rst,ci,co)
      t = ta + h*real(k) 
      R_IF = R_IF + (f1 + 2*f2  +2*f3 + f4)/6.0
      RIF2(k)=R_IF
  enddo
end subroutine rk4_c

