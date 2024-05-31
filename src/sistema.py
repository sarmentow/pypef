from dataclasses import dataclass, field
from enum import Enum
import numpy as np
import numpy as np

@dataclass
class vec3:
    x: float
    y: float
    z: float

    '''
    Suporte para acessar componentes usando índices:
        a = vec3(1, 0, 2)
        a[0] -> 1
        a[1] -> 0
        a[2] -> 2
    '''
    def __getitem__(self, key: int) -> float:
        match key:
            case 0: return self.x
            case 1: return self.y
            case 2: return self.z
            case _: raise IndexError 

    def __setitem__(self, key: int, val: float) -> None:
        match key:
            case 0: self.x = val
            case 1: self.y = val
            case 2: self.z = val
            case _: raise IndexError 
    
    def __str__(self):
        return f"{self.x}i + {self.y}j + {self.z}k"

 

@dataclass
class vec3bool:
    x: bool
    y: bool
    z: bool

    '''
    Suporte para acessar componentes usando índices:
        a = vec3bool(False, True, False)
        a[0] -> False
        a[1] -> True
        a[2] -> False
    '''
    def __getitem__(self, key: int) -> bool:
        match key:
            case 0: return self.x
            case 1: return self.y
            case 2: return self.z
            case _: raise IndexError 

@dataclass
class Vinculo:
    f_restriction: vec3bool = vec3bool(False, False, False)
    m_restriction: vec3bool = vec3bool(False, False, False)

class Vinculos:
    ApoioSimplesX = Vinculo(f_restriction=vec3bool(True, False, False))
    ApoioSimplesY = Vinculo(f_restriction=vec3bool(False, True, False))
    ApoioSimplesZ = Vinculo(f_restriction=vec3bool(False, False, True))
    Articulacao = Vinculo(f_restriction=vec3bool(True, True, True))
    Engaste = Vinculo(f_restriction=vec3bool(True, True, True), m_restriction=vec3bool(True, True, True))
    Nulo = Vinculo(f_restriction= vec3bool(False, False, False), m_restriction= vec3bool(False, False, False))


class Ponto:
    def __init__(self, pos: vec3, vinculo: Vinculo):
        self.pos= pos
        self.vinculo = vinculo
        self.f: vec3 = vec3(0, 0, 0)
        self.m: vec3 = vec3(0, 0, 0)

@dataclass
class CargaPontual:
    pos: vec3
    f: vec3

@dataclass
class Momento:
    m: vec3

class Barra:

    def __init__(self, p0: Ponto, p1: Ponto):
        self.p0 = p0
        self.p1 = p1
        # Tirar cargas e momentos da barra e colocar no Sistema
        self.cargas: list[CargaPontual] = []
        self.momentos: list[Momento] = []

    def add_carga(self, c: CargaPontual) -> None:
        self.cargas.append(c)


    def add_momento(self, c: Momento) -> None:
        self.momentos.append(c)


'''
Representa a estrutura que queremos resolver.

Presumimos um sistema isostático válido. O programa não tenta validar o sistema que recebe.

Lixo in, lixo out. 

TODO: implementar Viga Gerber
TODO: implementar função que permita adicionar várias barras de uma vez
'''

class Sistema:

    def __init__(self):
        self.barras: list[Barra] = []
        self.resolvido: bool = False
        self.coeff: np.ndarray = None
        self.ind: np.ndarray = None
        self.variaveis: np.ndarray = None
        
    
    def print_reactions(self):
        for idx, b in enumerate(self.barras):
            print(f"Reações da barra {idx}:")
            print(f"p0: F = {b.p0.f}, M = {b.p0.m}")
            print(f"p1: F = {b.p1.f}, M = {b.p1.m}")

    '''
    Resolve o sistema de equações formado pelas barras. 

    O algoritmo monta a matriz de coeficientes do sistema linear e a resolve. 
    '''
    def resolver_sistema(self) -> None:

        variaveis: np.ndarray = None

        '''
        Cada ponto tem 6 variáveis (3 componentes de f e 3 componentes de m)
        Cada barra tem 2 pontos.
        O sistema fica com 6 fileiras (1 para cada componente de f e m)
        E (6 x 2 x barras) colunas
        ''' 

        self.coeff = np.zeros((6, 6 * 2 * len(self.barras)))
        self.ind = np.zeros(6)

        ''''
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

        # 1. Equilíbrio das forças 
        for eixo_f in range(3):
            for idx, b in enumerate(self.barras):
                self.coeff[eixo_f][12*idx + eixo_f] = b.p0.vinculo.f_restriction[eixo_f]
                self.coeff[eixo_f][12*idx + eixo_f + 6] = b.p1.vinculo.f_restriction[eixo_f]
                ''' 
                Como coeff = np.zeros, implicitamente, tudo que não teve valor atribuido tem valor zero.
                '''
                for carga in b.cargas:
                    self.ind[eixo_f] += -carga.f[eixo_f]
        
        # 2. Equilíbrio dos momentos
        for idx_eixo_m in range(3, 6):
            eixo_m = idx_eixo_m - 3
            for idx, b in enumerate(self.barras):
                # Primeiro consideramos os momentos gerados pelos próprios vínculos 
                self.coeff[idx_eixo_m][12*idx + eixo_m + 3] = b.p0.vinculo.m_restriction[eixo_m]
                self.coeff[idx_eixo_m][12*idx + eixo_m + 9] = b.p1.vinculo.m_restriction[eixo_m]

                
        # Depois precisamos considerar os momentos de cada força do sistema com relação à origem (polo arbitrário)`
        for idx, b in enumerate(self.barras):
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

            # TODO Agora calcular para as caragas pontuais de cada barra
            # TODO melhorar eficiencia :) 
            result = np.array([0., 0., 0.])
            for carga in b.cargas:
                result += np.cross([carga.pos.x, carga.pos.y, carga.pos.z], [carga.f.x, carga.f.y, carga.f.z])

            # TODO Incluir momentos no termo independente.
            for momento in b.momentos:
                result += np.array([momento.m.x, momento.m.y, momento.m.z])
            
            self.ind[3:6] += -result

        # Remove colunas preenchidas inteiramente com 0 que não participarão do sistema linear 
        # TODO try except
        self.coeff = self.coeff[:, ~np.all(self.coeff == 0, axis=0)]
        self.variaveis = np.linalg.solve(self.coeff, self.ind)

        iVar = 0

        for idx, b in enumerate(self.barras):
            for eixo in range(3):
                if(b.p0.vinculo.f_restriction[eixo]):
                    b.p0.f[eixo] = self.variaveis[iVar]
                    iVar = iVar + 1
                if(b.p1.vinculo.f_restriction[eixo]):
                    b.p1.f[eixo] = self.variaveis[iVar]
                    iVar = iVar + 1
        
        for idx, b in enumerate(self.barras):
            for eixo in range(3):
                if(b.p0.vinculo.m_restriction[eixo]):
                    b.p0.m[eixo] = self.variaveis[iVar]
                    iVar = iVar + 1
                if(b.p1.vinculo.m_restriction[eixo]):
                    b.p1.m[eixo] = self.variaveis[iVar]
                    iVar = iVar + 1

        self.resolvido = True
        
    def add_barra(self, b: Barra) -> None:
            self.barras.append(b)

    
s = Sistema()
b0 = Barra(Ponto(vec3(0, 0, 0), Vinculos.Engaste), Ponto(vec3(4, 0, 0), Vinculos.Nulo))
b0.add_momento(Momento(vec3(0, 2000, 0)))
b1 = Barra(Ponto(vec3(4, 0, 0), Vinculos.Nulo), Ponto(vec3(4, 0, -1), Vinculos.Nulo))
b2 = Barra(Ponto(vec3(4, 0, -1), Vinculos.Nulo), Ponto(vec3(4, -2, -1), Vinculos.Nulo))
b2.add_carga(CargaPontual(vec3(4, -2, -1), vec3(-2, 0, -1)))
s.resolver_sistema()
s.print_reactions()