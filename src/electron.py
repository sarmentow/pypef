# Para evitar que pequenos problemas de versionamento impeçam a gui de rodar.
import sys
import warnings
warnings.filterwarnings("ignore")

import json
from elementos_estruturais import *
from utils import *
from portico_plano import *



s_str_raw = input()
s_raw = json.loads(s_str_raw)
#print(s_raw)
s = Sistema()

def ponto_from_raw(i, nulo=False):
    x = i['x']
    y = i['y']
    # TODO editor only supports 2d, implement 3d
    z = 0
    fx = i['Vinculo']['f']['x']
    fy = i['Vinculo']['f']['y']
    fz = i['Vinculo']['f']['z']
    mx = i['Vinculo']['m']['x']
    my = i['Vinculo']['m']['y']
    mz = i['Vinculo']['m']['z']
    return Ponto(x, y, z, Vinculos.Nulo if nulo else Vinculo(vec3bool(fx, fy, fz), vec3bool(mx, my, mz)))


'''
A ideia aqui é que mandamos o primeiro e segundo vértices "Normalmente"
Depois disso, você descarta o vínculo do primeiro sempre, para não termos vínculos duplos
'''
barras = []
p0 = ponto_from_raw(s_raw['vertices'][0])
p1 = ponto_from_raw(s_raw['vertices'][1])
barras.append(Barra(p0, p1))
# Adicionar barras/vinculos
for idx, i in enumerate(s_raw['vertices']):
    if idx < 2: continue
    p0 = ponto_from_raw(s_raw['vertices'][idx - 1], nulo=True)
    p1 = ponto_from_raw(i)
    barras.append(Barra(p0, p1))

s.add_barra(barras)

def carga_from_raw(i) -> CargaPontual:
    x = i['pos']['x']
    y = i['pos']['y']
    z = i['pos']['z']
    fx = i['f']['x']
    fy = i['f']['y']
    fz = i['f']['z']
    return CargaPontual(x, y, z, fx, fy, fz)

# Adicionar cargas
cargas: list[CargaPontual] = []
for idx, i in enumerate(s_raw['cargas']):
    cargas.append(carga_from_raw(i))

s.add_carga(cargas)
p = PorticoPlano(s)
p.resolver_sistema()
#p.print_reactions()

'''
JSON obj format response for
[0, 0, 0, 0]
[{f: [0, 0, 0], m: [0, 0, 0]}, ...]
array of objects
each object at index i represents

filter vinculo nulo
'''

pre_json = []

def json_vertex(p: Ponto) -> dict:
    return dict({'f': [p.f.x, p.f.y, p.f.z], 'm': [p.m.x, p.m.y, p.m.z]})

for barra in p.sistema.barras:
    if barra.p0.vinculo != Vinculos.Nulo: pre_json.append(json_vertex(barra.p0))
    if barra.p1.vinculo != Vinculos.Nulo: pre_json.append(json_vertex(barra.p1))

sys.stdout.write(json.dumps(pre_json))