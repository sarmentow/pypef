from elementos_estruturais import *
import numpy as np

'''
TODO melhorar eficiencia
TODO try except
'''

'''
Layout da matrix do sistema linear (consideramos o momento com relação à origem, sempre):

        | B0_P0_Fx          B0_P0_Fy          B0_P0_Fz          B0_P0_Mx          B0_P0_My          B0_P0_Mz          ...Same for P1... Bi_P0_Fx          Bi_P0_Fy          Bi_P0_Fz          Bi_P0_Mx          Bi_P0_My          Bi_P0_Mz          |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
Eq. Fx  | B0_P0.v.f.x       0                 0                 0                 0                 0                 ...Same for P1... Bi_P0.v.f.x       0                 0                 0                 0                 0                 |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
Eq. Fy  | 0                 B0_P0.v.f.y       0                 0                 0                 0                 ...Same for P1... 0                 Bi_P0.v.f.y       0                 0                 0                 0                 |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
Eq. Fz  | 0                 0                 B0_P0.v.f.z       0                 0                 0                 ...Same for P1... 0                 0                 Bi_P0.v.f.z       0                 0                 0                 |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
Eq. Mx  | 0                 B0_P0.pos.z       -B0_P0.pos.y      B0_P0.v.f.Mx      0                 0                 ...Same for P1... 0                 Bi_P0.pos.z       -Bi_P0.pos.y      Bi_P0.v.f.Mx      0                 0                 |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
Eq. My  | -B0_P0.pos.z      0                 B0_P0.pos.x       0                 B0_P0.v.f.My      0                 ...Same for P1... -Bi_P0.pos.z      0                 Bi_P0.pos.x       0                 Bi_P0.v.f.My      0                 |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
Eq. Mz  | B0_P0.pos.y       -B0_P0.pos.x      0                 0                 0                 B0_P0.v.f.Mz      ...Same for P1... Bi_P0.pos.y       -Bi_P0.pos.x      0                 0                 0                 Bi_P0.v.f.Mz      |
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|

Como consideramos apenas estruturas isostáticas, esse sistema terá várias colunas zeradas, o que nos permitirá retirar colunas até chegar numa matriz 6x6, ou seja, um sistema possível e determinado.
'''

class PorticoPlano:

    def __init__(self, s: Sistema):
        self.sistema: Sistema = s
        self.resolvido: bool = False
        self.coeff: np.ndarray = None
        self.ind: np.ndarray = None
        self.variaveis: np.ndarray = None
        
    def print_reactions(self):
        for idx, b in enumerate(self.sistema.barras):
            print(f"Reações da barra {idx}:")

            print(b.p0.f)

            print(b.p0.f.module())

            if b.p0.f.module() != 0 or b.p0.m.module() != 0:
                print(f"p0: F = {b.p0.f}, M = {b.p0.m}")
            else:
                print(f"p0: Reação nula")

            if b.p1.f.module() != 0 or b.p1.m.module() != 0:
                print(f"p1: F = {b.p1.f}, M = {b.p1.m}")
            else:
                print(f"p1: Reação nula")

    def resolver_sistema(self) -> None:

        self.coeff = np.zeros((6, 6 * 2 * len(self.sistema.barras)))
        self.ind = np.zeros(6)

        # 1. Equilíbrio das forças 
        for eixo_f in range(3):
            for idx, b in enumerate(self.sistema.barras):
                self.coeff[eixo_f][12*idx + eixo_f] = b.p0.vinculo.f_restriction[eixo_f]
                self.coeff[eixo_f][12*idx + eixo_f + 6] = b.p1.vinculo.f_restriction[eixo_f]
                ''' 
                Como coeff = np.zeros, implicitamente, tudo que não teve valor atribuido tem valor zero.
                '''
            for carga in self.sistema.cargas:
                self.ind[eixo_f] += -carga.f[eixo_f]
        
        # 2. Equilíbrio dos momentos
        for idx_eixo_m in range(3, 6):
            eixo_m = idx_eixo_m - 3
            for idx, b in enumerate(self.sistema.barras):
                # Primeiro consideramos os momentos gerados pelos próprios vínculos 
                self.coeff[idx_eixo_m][12*idx + eixo_m + 3] = b.p0.vinculo.m_restriction[eixo_m]
                self.coeff[idx_eixo_m][12*idx + eixo_m + 9] = b.p1.vinculo.m_restriction[eixo_m]

                
        # Depois precisamos considerar os momentos de cada força do sistema com relação à origem (polo arbitrário)`
        for idx, b in enumerate(self.sistema.barras):
            # Mx
            self.coeff[3][12*idx + 1] = -b.p0.pos.z * b.p0.vinculo.f_restriction.y
            self.coeff[3][12*idx + 2] = b.p0.pos.y * b.p0.vinculo.f_restriction.z
            self.coeff[3][12*idx + 3] = b.p0.vinculo.m_restriction.x

            self.coeff[3][12*idx + 1 + 6] = -b.p1.pos.z * b.p1.vinculo.f_restriction.y
            self.coeff[3][12*idx + 2 + 6] = b.p1.pos.y * b.p1.vinculo.f_restriction.z
            self.coeff[3][12*idx + 3 + 6] = b.p1.vinculo.m_restriction.x

            #My
            self.coeff[4][12*idx] = b.p0.pos.z * b.p0.vinculo.f_restriction.x
            self.coeff[4][12*idx + 2] = -b.p0.pos.x * b.p0.vinculo.f_restriction.z
            self.coeff[4][12*idx + 4] = b.p0.vinculo.m_restriction.y

            self.coeff[4][12*idx + 6] = b.p1.pos.z * b.p1.vinculo.f_restriction.x
            self.coeff[4][12*idx + 2 + 6] = -b.p1.pos.x * b.p1.vinculo.f_restriction.z
            self.coeff[4][12*idx + 4 + 6] = b.p1.vinculo.m_restriction.y

            #Mz
            self.coeff[5][12*idx] = -b.p0.pos.y * b.p0.vinculo.f_restriction.x
            self.coeff[5][12*idx + 1] = b.p0.pos.x * b.p0.vinculo.f_restriction.y
            self.coeff[5][12*idx + 5] = b.p0.vinculo.m_restriction.z

            self.coeff[5][12*idx + 6] = -b.p1.pos.y * b.p1.vinculo.f_restriction.x
            self.coeff[5][12*idx + 1 + 6] = b.p1.pos.x * b.p1.vinculo.f_restriction.y
            self.coeff[5][12*idx + 5 + 6] = b.p1.vinculo.m_restriction.z


            result = np.array([0., 0., 0.])
        for carga in self.sistema.cargas:
            result += np.cross([carga.pos.x, carga.pos.y, carga.pos.z], [carga.f.x, carga.f.y, carga.f.z])

        for momento in self.sistema.momentos:
            result += np.array([momento.m.x, momento.m.y, momento.m.z])
            
        self.ind[3:6] += -result

        # Remove linhas e colunas LD
        self.coeff = self.coeff[:, ~np.all(self.coeff == 0, axis=0)]
        
        all_zeros = np.all(self.coeff == 0, axis=1)
        indexes_zeros = np.where(all_zeros)[0]

        coeff_treated = np.delete(self.coeff, indexes_zeros, axis=0)
        ind_treated = np.delete(self.ind, indexes_zeros, axis=0)

        self.variaveis = np.linalg.solve(coeff_treated, ind_treated)

        iVar = 0

        for idx, b in enumerate(self.sistema.barras):
            for eixo in range(3):
                if(b.p0.vinculo.f_restriction[eixo]):
                    if len(np.where(indexes_zeros == eixo)) == 0:
                        b.p0.f[eixo] = self.variaveis[iVar]
                        iVar = iVar + 1
                if(b.p1.vinculo.f_restriction[eixo]):
                    if len(np.where(indexes_zeros == eixo)) == 0:
                        b.p1.f[eixo] = self.variaveis[iVar]
                        iVar = iVar + 1
        
        for idx, b in enumerate(self.sistema.barras):
            for eixo in range(3):
                if(b.p0.vinculo.m_restriction[eixo]):
                    if len(np.where(indexes_zeros == eixo)) == 0:
                        b.p0.m[eixo] = self.variaveis[iVar]
                        iVar = iVar + 1
                if(b.p1.vinculo.m_restriction[eixo]):
                    if len(np.where(indexes_zeros == eixo)) == 0:
                        b.p1.m[eixo] = self.variaveis[iVar]
                        iVar = iVar + 1

        self.resolvido = True
        


s = Sistema()
inicio = Ponto(0, 0, 0, Vinculos.Engaste)
fim = Ponto(1, 0, 0, Vinculos.Nulo)
b = Barra(inicio, fim)
s.add_barra([b])
p = PorticoPlano(s)
p.resolver_sistema()
p.print_reactions()