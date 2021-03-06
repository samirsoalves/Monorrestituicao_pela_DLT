# importa as bibliotecas
from sympy import *
import numpy as np
from numpy.linalg import inv
np.set_printoptions(suppress=True)

############################### DADOS DE ENTRADA ###############################

# Coordenadas Geod�sicas dos pontos de apoio coletados NO TERRENO---------------

# Coordenadas dos PONTOS DE CONTROLE (Ordem dos dados: ID,X,Y,Z) utilizados na
# determeina��o dos par�metros da DLT linear no ajustamento param�trico pelo
# M�todo dos M�nimos Quadrados(MMQ)
pa_pc = np.array([[2,488.402,563.665,8.267],
                  [57,444.191,669.765,21.42],
                  [84,675.587,374.946,1.432],
                  [127,770.173,537.567,8.069],
                  [136,395.148,530.693,6.973],
                  [145,579.864,510.927,5.448]])

# Coordenadas dos PONTOS DE VERIFICA��O (Ordem dos dados: ID,X,Y,Z) utlizadas no
# p�s-ajustamento para avaliar os par�metros determinados por meio da DLT inversa
pa_pv = np.array([[94,525.366,492.427,7.269],
                 [108,554.357,662.66,12.16],
                 [123,669.969,577.359,9.741],
                 [129,648.682,432.527,2.117],
                 [133,585.134,476.260,3.493],
                 [138,395.067,588.307,8.878]])

# Coordenadas (COLUNA, LINHA) dos pontos de apoio NA IMAGEM---------------------

# Coordenadas dos PONTOS DE CONTROLE (ID dos pontos: 02,57,84,127,136,145)  
# utilizados como observa��es (vetor Lb) 
cl_pc = np.array([[863,1047],
       [129,315],
       [2684,1899],
       [3056,503],
       [278,1530],
       [1689,1197]])

# Coordenadas dos PONTOS DE VERIFICA��O (ID dos pontos: 94,108,123,129,133,138)
cl_pv = np.array([[1337,1476],
         [1074,88],
         [2206,456],
         [2370,1575],
         [1816,1432],
         [84,1110]])

# Dimens�o do pixel no sensor em mil�metros convertida para metro---------------
tpx = 0.007/1000
tpy = 0.007/1000
tp= 0.007/1000

########################## AJUSTAMENTO DAS OBSERVA��ES #########################
########################## PELO MODELO PARAM�TRICO DO ##########################
######################### M�TODO DOS M�NIMOS QUADRADOS #########################

# Modelo funcional colinaridade-------------------------------------------------
# DLT linear
# x,y = coordenadas dos pontos de apoio na imagem
# X,Y,Z = coordenadas Geod�sicas em campo
# L1,L2,...,L11 = Par�metros da DLT
# OBS: xp=x e yp=y
L1,L2,L3,L4,L5,L6,L7,L8,L9,L10,L11,x,y,X, Y, Z = symbols('L1 L2 L3 L4 L5 L6 L7 L8 L9 L10 L11 x y X Y Z')

xp = L1*X + L2*Y + L3*Z + L4 - x*L9*X - x*L10*Y - x*L11*Z
yp = L5*X + L6*Y + L7*Z + L8 - y*L9*X - y*L10*Y - y*L11*Z

dad=np.column_stack([cl_pc,pa_pc])

# Matriz Peso (P)---------------------------------------------------------------
# utilizando a dimens�o do pixel 
I=np.identity(12, dtype=float)
P=I*(1/((tp)**2))
P=np.matrix(P)

# Matriz A ---------------------------------------------------------------------
# fun��o para montagem da matriz das derivadas da DLT em fun��o dos par�metros 
def matrizA(dad,xp,yp):  
    a1 = diff(xp,L1)
    a2 = diff(xp,L2)
    a3 = diff(xp,L3)
    a4 = diff(xp,L4)
    a5 = diff(xp,L5)
    a6 = diff(xp,L6)
    a7 = diff(xp,L7)
    a8 = diff(xp,L8)
    a9 = diff(xp,L9)
    a10 = diff(xp,L10)
    a11 = diff(xp,L11)
    
    a12 = diff(yp,L1)
    a13 = diff(yp,L2)
    a14 = diff(yp,L3)
    a15 = diff(yp,L4)
    a16 = diff(yp,L5)
    a17 = diff(yp,L6)
    a18 = diff(yp,L7)
    a19 = diff(yp,L8)
    a20 = diff(yp,L9)
    a21 = diff(yp,L10)
    a22 = diff(yp,L11)
    
    coef_x = [a1, a2, a3, a4, a5, a6, a7, a8, a9, a10, a11]
    coef_y = [a12, a13, a14, a15, a16, a17, a18, a19, a20, a21, a22]
    
    def IterA(coef,dad):
        val_A=[]
        for i in dad:
            for j in coef:
                num_a = j.evalf(subs={X: i[3], Y: i[4],\
                                      Z: i[5], x: i[0], y: i[1]})
                val_A=np.append(val_A,num_a)
        return val_A       
    
    val_Ax=IterA(coef_x,dad)
    val_Ay=IterA(coef_y,dad)
    
    A=np.matrix([val_Ax[0:11], val_Ay[0:11], val_Ax[11:22], val_Ay[11:22],\
                val_Ax[22:33], val_Ay[22:33],val_Ax[33:44],val_Ay[33:44],\
                val_Ax[44:55], val_Ay[44:55], val_Ax[55:66], val_Ay[55:66]])
    return A

#Matriz A-----------------------------------------------------------------------
A=matrizA(dad,xp,yp).astype(np.float)       
At = np.transpose(A)

# Vetor das observa��es (Lb)----------------------------------------------------
pts_pc=[]
for i in cl_pc:
    pts_pc=np.append(pts_pc,(np.array([i[0],i[1]])))
Lb=np.matrix(pts_pc)
Lb=np.transpose(Lb)

# Vetor dos par�mtros ajustados (Xa)--------------------------------------------
Xa=inv(At*P*A)*At*P*Lb

# Vetor dos Res�duos (V)--------------------------------------------------------
V=A*Xa-Lb

# Sigma posteriori--------------------------------------------------------------
n=len(Lb) # n�mero de observa��es 
u=len(Xa) # n�mero de par�metros determinados
Vt=np.transpose(V)
sigma_pos=Vt*P*V/(n-u)

# MCV dos Par�metros ajustados--------------------------------------------------
mvc_p=float(sigma_pos)*inv(At*P*A)

# MVC das observa��es ajustadas-------------------------------------------------
mvc_vaj=A*inv(At*P*A)*At

################################ MONORESTITUI��O ###############################
# Determina��o de coordenadas geod�sicas X,Y,Z a partir dos par�metros ajustados
# utilizando a DLT Inversa e dos valores de coluna e linha dos pontos
xa=np.array(Xa) # par�metros ajustados 
d=np.column_stack([cl_pv,pa_pv]) 

# c�lculo das coordenas X,Y,Z---------------------------------------------------
pa_pv_cal=[] 
for k in d:  # pontos calculados
    a11=xa[0][0]-k[0]*xa[8][0]
    a12=xa[1][0]-k[0]*xa[9][0]
    a21=xa[4][0]-k[1]*xa[8][0]
    a22=xa[5][0]-k[1]*xa[9][0]
    c11=-k[5]*(xa[2][0]-k[0]*xa[10][0])-xa[3][0]+k[0]
    c12=-k[5]*(xa[6][0]-k[1]*xa[10][0])-xa[7][0]+k[1]
    AA=np.matrix([[float(a11), float(a12)], [float(a21), float(a22)]])
    C=np.matrix([[float(c11)], [float(c12)]])
    pa_pvcal=np.dot(inv(AA),C)
    pa_pv_cal=np.append(pa_pv_cal,pa_pvcal)

# Compara��o das coordenadas calculadas na mono restitui��o e as levantadas em 
# campo (pontos de verifica��o)-------------------------------------------------
pa_pv_vetor=[] 
for i in pa_pv: # pontos de verifica��o levandos em campo
    X=i[1]
    Y=i[2]
    pa_pv_vetor=np.append(pa_pv_vetor,np.array([X,Y]))

pa_pv_dif=pa_pv_cal-pa_pv_vetor

print(pa_pv_dif)

########################### AVALIA��O DO AJUSTAMENTO ###########################
# avalia��o do sigma posteriori (n�vel de signific�ncia = 5%)-------------------
Qui_cal=Vt*P*V
Qui_tab_025=0.001
Qui_tab_975=5.024

# avalia��o da signific�ncia dos par�metros (n�vel de signific�ncia = 5%)-------
diag_mvc_p =np.array([row[i] for i,row in enumerate(np.array(mvc_p))])

for i in range(0,len(Xa),1):
    valor_t_cal=abs(Xa[i][0])/((diag_mvc_p[i])**(1/2))

valor_t_tab=6.314