from utils import *

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
    def __init__(self, x: float, y: float, z: float, vinculo: Vinculo):
        self.pos= vec3(x, y, z)
        self.vinculo = vinculo
        self.f: vec3 = vec3(0, 0, 0)
        self.m: vec3 = vec3(0, 0, 0)

class CargaPontual:
    def __init__(self, pos_x: float, pos_y: float, pos_z: float, f_x: float, f_y: float, f_z: float) -> None:
       self.pos = vec3(pos_x, pos_y, pos_z)
       self.pos = vec3(f_x, f_y, f_z)

class Momento:
    def __init__(self, x: float, y: float, z: float) -> None:
        m = vec3 (x, y, z)

class Barra:
    def __init__(self, p0: Ponto, p1: Ponto):
        self.p0 = p0
        self.p1 = p1
        # Tirar cargas e momentos da barra e colocar no Sistema
        self.cargas: list[CargaPontual] = []
        self.momentos: list[Momento] = []

    def add_carga(self, c: CargaPontual) -> None:
        self.cargas.append(c)

    def add_carga(self, cargas: list[CargaPontual]) -> None:
        for c in cargas:
            self.cargas.append(c)

    def add_momento(self, m: Momento) -> None:
        self.momentos.append(m)

    def add_momento(self, momentos: list[Momento]) -> None:
        for m in momentos:
            self.momentos.append(m)