from utils import vec3, vec3bool
import scipy.integrate as integrate
from dataclasses import dataclass

@dataclass
class Vinculo:
    f_restriction: vec3bool = vec3bool(False, False, False)
    m_restriction: vec3bool = vec3bool(False, False, False)

    def __str__(self):
        return f"{self.f_restriction}, {self.m_restriction}"

    def __eq__(self, other):
        return self.f_restriction == other.f_restriction and self.m_restriction == other.m_restriction

class Vinculos:
    ApoioSimplesX = Vinculo(f_restriction=vec3bool(True, False, False))
    ApoioSimplesY = Vinculo(f_restriction=vec3bool(False, True, False))
    ApoioSimplesZ = Vinculo(f_restriction=vec3bool(False, False, True))
    Articulacao = Vinculo(f_restriction=vec3bool(True, True, True))
    Engaste = Vinculo(f_restriction=vec3bool(True, True, True), m_restriction=vec3bool(True, True, True))
    Nulo = Vinculo(f_restriction= vec3bool(False, False, False), m_restriction= vec3bool(False, False, False))

class Ponto:
    def __init__(self, x: float, y: float, z: float, vinculo: Vinculo):
        self.pos= vec3(x, y, z)
        self.vinculo = vinculo
        self.f: vec3 = vec3(0, 0, 0)
        self.m: vec3 = vec3(0, 0, 0)

    def __str__(self):
        return f"Ponto em {self.pos}, vinculo {self.vinculo}"

class CargaPontual:
    def __init__(self, pos_x: float, pos_y: float, pos_z: float, f_x: float, f_y: float, f_z: float) -> None:
       self.pos = vec3(pos_x, pos_y, pos_z)
       self.f = vec3(f_x, f_y, f_z)

    # def __init__(self, pos:vec3, f:vec3):
    #     self.pos = pos
    #     self.f = f

class CargaDistribuida:
    def __init__(self, x0: float, y0:float , z0: float, x1: float, y1: float, z1: float, func) -> None:
        self.baricentro: vec3 = (vec3(x1, y1, z1) - vec3(x0, y0, z0))/2
        
        fx = integrate.quad(func, x0, x1)
        fy = integrate.quad(func, y0, y1)
        fz = integrate.quad(func, z0, z1)

        self.carga =  CargaPontual(self.baricentro, vec3(fx, fy, fz))

class Momento:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.m = vec3(x, y, z)

class Barra:
    def __init__(self, p0: Ponto, p1: Ponto):
        self.p0 = p0
        self.p1 = p1

    def __str__(self):
        return f"Barra - p0: {self.p0}, p1: {self.p1}"

class Sistema:
    def __init__(self) -> None: 
        self.barras: list[Barra] = []
        self.cargas: list[CargaPontual] = []
        self.momentos: list[Momento] = []
        
    def add_barra(self, b: Barra) -> None:
        self.barras.append(b)

    def add_barra(self, barras: list[Barra]) -> None:
        for b in barras:
            self.barras.append(b)

    # def add_carga(self, c: CargaPontual) -> None:
    #     self.cargas.append(c)

    def add_carga(self, cargas: list[CargaPontual]) -> None:
        for c in cargas:
            self.cargas.append(c)

    # def add_carga(self, c: CargaDistribuida) -> None:
    #     self.cargas.append(c)

    def add_momento(self, m: Momento) -> None:
        self.momentos.append(m)

    def add_momento(self, momentos: list[Momento]) -> None:
        for m in momentos:
            self.momentos.append(m)