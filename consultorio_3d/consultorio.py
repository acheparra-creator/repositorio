"""Modelo 3D del consultorio N1-07 (Tipo A, opcion C) a partir del plano A-03.

Todas las cotas en planta salen del PDF vectorial (escala 1:50), en metros.
Origen: esquina interior suroeste. X = este, Y = norte, Z = arriba.
Las alturas NO vienen en el plano: son supuestos (ver constantes).

Uso: python3 consultorio.py <carpeta_salida> [ancho_px] [muestras] [vistas,separadas,por,coma]
"""
import sys, math, random
import bpy
import numpy as np
from mathutils import Vector

OUT = sys.argv[1]
RESX = int(sys.argv[2]) if len(sys.argv) > 2 else 640
SAMPLES = int(sys.argv[3]) if len(sys.argv) > 3 else 32
ONLY = sys.argv[4].split(',') if len(sys.argv) > 4 else None

# ---------- cotas del plano (m) ----------
W, L = 3.686, 6.0            # interior
T = 0.15                     # espesor de muros
# ---------- supuestos de altura (no estan en el plano) ----------
H = 2.70                     # piso a losa
DOOR_H = 2.10

random.seed(7)
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col_main = scene.collection
col_ceil = bpy.data.collections.new('techo'); scene.collection.children.link(col_ceil)

# ---------------- materiales ----------------
def mat_new(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    return m, nt, b

def flat(name, color, rough=0.5, metal=0.0):
    m, nt, b = mat_new(name)
    b.inputs['Base Color'].default_value = (*color, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return m

def coords(nt, scale):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = scale
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    return mp

def concrete(name, c1, c2, bump=0.25):
    m, nt, b = mat_new(name)
    mp = coords(nt, (1, 1, 1))
    n1 = nt.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 1.6
    n1.inputs['Detail'].default_value = 8; n1.inputs['Roughness'].default_value = 0.65
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = 90
    n2.inputs['Detail'].default_value = 3
    nt.links.new(mp.outputs[0], n1.inputs['Vector']); nt.links.new(mp.outputs[0], n2.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB')
    r.color_ramp.elements[0].position = 0.3; r.color_ramp.elements[0].color = (*c1, 1)
    r.color_ramp.elements[1].position = 0.75; r.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(n1.outputs['Fac'], r.inputs['Fac'])
    nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.88
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = bump
    bp.inputs['Distance'].default_value = 0.002
    nt.links.new(n2.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def walnut(name, axis):
    """axis: eje de la veta (0=x,1=y,2=z)."""
    m, nt, b = mat_new(name)
    sc = [34, 34, 34]; sc[axis] = 1.6
    mp = coords(nt, tuple(sc))
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 1.0
    n.inputs['Detail'].default_value = 6; n.inputs['Roughness'].default_value = 0.6
    if 'Distortion' in n.inputs: n.inputs['Distortion'].default_value = 0.6
    nt.links.new(mp.outputs[0], n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB')
    e = r.color_ramp.elements
    e[0].position = 0.28; e[0].color = (0.055, 0.028, 0.014, 1)
    e[1].position = 0.72; e[1].color = (0.20, 0.105, 0.05, 1)
    mid = e.new(0.5); mid.color = (0.12, 0.062, 0.03, 1)
    nt.links.new(n.outputs['Fac'], r.inputs['Fac'])
    nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.42
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.08
    bp.inputs['Distance'].default_value = 0.001
    nt.links.new(n.outputs['Fac'], bp.inputs['Height'])
    nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m

def tile(name):
    m, nt, b = mat_new(name)
    mp = coords(nt, (1, 1, 1))
    br = nt.nodes.new('ShaderNodeTexBrick')
    br.inputs['Scale'].default_value = 1.0
    br.inputs['Brick Width'].default_value = 1.2
    br.inputs['Row Height'].default_value = 0.6
    br.inputs['Mortar Size'].default_value = 0.003
    br.inputs['Color1'].default_value = (0.235, 0.225, 0.208, 1)
    br.inputs['Color2'].default_value = (0.25, 0.24, 0.222, 1)
    br.inputs['Mortar'].default_value = (0.09, 0.088, 0.085, 1)
    nt.links.new(mp.outputs[0], br.inputs['Vector'])
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2.5; n.inputs['Detail'].default_value = 8
    nt.links.new(mp.outputs[0], n.inputs['Vector'])
    mx = nt.nodes.new('ShaderNodeMixRGB'); mx.blend_type = 'MULTIPLY'; mx.inputs['Fac'].default_value = 0.35
    nt.links.new(br.outputs['Color'], mx.inputs['Color1']); nt.links.new(n.outputs['Color'], mx.inputs['Color2'])
    nt.links.new(mx.outputs[0], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.45
    return m

def emit(name, color, strength):
    m, nt, b = mat_new(name)
    b.inputs['Base Color'].default_value = (0, 0, 0, 1)
    b.inputs['Emission Color'].default_value = (*color, 1)
    b.inputs['Emission Strength'].default_value = strength
    return m

def glass(name):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    g = nt.nodes.new('ShaderNodeBsdfGlossy'); g.inputs['Roughness'].default_value = 0.0
    t = nt.nodes.new('ShaderNodeBsdfTransparent'); t.inputs['Color'].default_value = (0.94, 0.96, 0.95, 1)
    fr = nt.nodes.new('ShaderNodeFresnel'); fr.inputs['IOR'].default_value = 1.45
    mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(fr.outputs[0], mx.inputs[0]); nt.links.new(t.outputs[0], mx.inputs[1]); nt.links.new(g.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface'])
    return m

WARM = (1.0, 0.62, 0.32)     # ~3000 K
M = dict(
    conc=concrete('concreto', (0.20, 0.195, 0.185), (0.30, 0.29, 0.275)),
    conc_ceil=concrete('concreto_techo', (0.19, 0.185, 0.18), (0.26, 0.255, 0.245), 0.15),
    greige=flat('greige', (0.37, 0.345, 0.305), 0.9),
    wal_z=walnut('nogal_vertical', 2), wal_y=walnut('nogal_y', 1), wal_x=walnut('nogal_x', 0),
    tile=tile('porcelanato'),
    quartz=flat('cuarzo', (0.66, 0.62, 0.55), 0.3),
    black=flat('negro_mate', (0.012, 0.012, 0.012), 0.45),
    dark=flat('antracita', (0.03, 0.03, 0.032), 0.7),
    steel=flat('acero', (0.45, 0.45, 0.45), 0.3, 1.0),
    leather=flat('piel_carbon', (0.03, 0.03, 0.032), 0.42),
    fab_dark=flat('tela_gris_oscuro', (0.07, 0.07, 0.072), 0.95),
    fab_greige=flat('tela_greige', (0.48, 0.45, 0.40), 0.95),
    leaf=flat('hoja', (0.045, 0.11, 0.035), 0.5),
    trunk=flat('tronco', (0.10, 0.07, 0.045), 0.8),
    soil=flat('tierra', (0.03, 0.022, 0.015), 1.0),
    screen=flat('pantalla', (0.004, 0.004, 0.005), 0.08),
    amber=flat('ambar', (0.20, 0.07, 0.01), 0.15),
    led=emit('led', WARM, 22), led_soft=emit('led_suave', WARM, 9), spot=emit('spot', (1.0, 0.75, 0.5), 30),
    glass=glass('vidrio'),
    patio_wall=flat('muro_patio', (0.36, 0.345, 0.32), 0.9),
    patio_floor=flat('piso_patio', (0.33, 0.32, 0.30), 0.8),
)
BOOKS = [flat('libro%d' % i, c, 0.7) for i, c in enumerate(
    [(0.05, 0.05, 0.05), (0.42, 0.39, 0.34), (0.16, 0.10, 0.06), (0.30, 0.30, 0.29), (0.09, 0.09, 0.10), (0.55, 0.51, 0.45)])]

# ---------------- geometria ----------------
HIDE_IN_PLAN = []
def box(name, x0, x1, y0, y1, z0, z1, mat, bevel=0.0, coll=None, smooth=False):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    if name.startswith(('sup_', 'led_nicho', 'led_bajo', 'libro', 'nicho_')): HIDE_IN_PLAN.append(o)
    me = o.data
    for v in me.vertices:
        v.co = Vector((x0 if v.co.x < 0 else x1, y0 if v.co.y < 0 else y1, z0 if v.co.z < 0 else z1))
    o.location = (0, 0, 0)
    me.materials.append(M[mat] if isinstance(mat, str) else mat)
    if bevel > 0:
        md = o.modifiers.new('bevel', 'BEVEL'); md.width = bevel; md.segments = 4 if smooth else 2
        if smooth:
            for p in me.polygons: p.use_smooth = True
            md.harden_normals = True
    if coll is not None:
        for c in o.users_collection: c.objects.unlink(o)
        coll.objects.link(o)
    return o

def cyl(name, x, y, z0, z1, r, mat, verts=32, r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r if r2 is None else r2,
                                    depth=z1 - z0, location=(x, y, (z0 + z1) / 2))
    o = bpy.context.active_object; o.name = name
    o.data.materials.append(M[mat] if isinstance(mat, str) else mat)
    for p in o.data.polygons: p.use_smooth = len(p.vertices) == 4
    return o

def tube(name, pts, r, mat):
    cu = bpy.data.curves.new(name, 'CURVE'); cu.dimensions = '3D'
    sp = cu.splines.new('NURBS'); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts): p.co = (*c, 1)
    sp.use_endpoint_u = True; sp.order_u = 3
    cu.bevel_depth = r; cu.bevel_resolution = 6; cu.resolution_u = 16
    o = bpy.data.objects.new(name, cu); col_main.objects.link(o)
    cu.materials.append(M[mat]); return o

def foliage(name, center, radii, n, size=0.06, mat='leaf'):
    cx, cy, cz = center; verts = []; faces = []
    for i in range(n):
        while True:
            p = np.random.uniform(-1, 1, 3)
            if 0.25 < np.linalg.norm(p) <= 1: break
        pos = np.array([cx + p[0] * radii[0], cy + p[1] * radii[1], cz + p[2] * radii[2]])
        a = np.random.normal(size=3); a /= np.linalg.norm(a)
        b = np.cross(a, np.random.normal(size=3)); b /= np.linalg.norm(b)
        s = size * np.random.uniform(0.7, 1.3)
        k = len(verts)
        verts += [tuple(pos - a * s), tuple(pos + b * s * 0.38), tuple(pos + a * s), tuple(pos - b * s * 0.38)]
        faces.append((k, k + 1, k + 2, k + 3))
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces)
    o = bpy.data.objects.new(name, me); col_main.objects.link(o); me.materials.append(M[mat]); return o

np.random.seed(3)

# ---- piso, losa ----
box('piso', 0, W, 0, L, -0.1, 0, 'tile')
box('losa', -T, W + T, -T, L + T, H, H + 0.15, 'conc_ceil', coll=col_ceil)

# ---- muros perimetrales ----
box('muro_oeste', -T, 0, -T, L + T, 0, H, 'greige')
box('muro_este', W, W + T, -T, L + T, 0, H, 'conc')
# muro norte con vano de puerta x 0.30-1.20
box('muro_norte_a', 0, 0.30, L, L + T, 0, H, 'greige')
box('muro_norte_b', 1.20, W, L, L + T, 0, H, 'greige')
box('dintel_entrada', 0.30, 1.20, L, L + T, DOOR_H, H, 'greige')
box('puerta_entrada', 0.30, 1.20, L + 0.02, L + 0.06, 0, DOOR_H, 'wal_z')
box('puerta_entrada_tapa', 0.30, 1.20, L + 0.06, L + T, 0, DOOR_H, 'dark')
box('manija_entrada', 1.08, 1.10, L - 0.03, L + 0.02, 1.0, 1.15, 'black')

# ---- bano (muros segun plano; puerta dibujada cerrada) ----
box('muro_bano_sur', 1.90, W, 4.80, 4.90, 0, H, 'greige')
box('bano_jamba_s', 1.80, 1.90, 4.80, 4.90, 0, H, 'greige')
box('bano_jamba_n', 1.80, 1.90, 5.80, 6.00, 0, H, 'greige')
box('bano_dintel', 1.80, 1.90, 4.90, 5.80, DOOR_H, H, 'greige')
box('puerta_bano', 1.83, 1.87, 4.90, 5.80, 0, DOOR_H, 'wal_z')
box('manija_bano', 1.78, 1.83, 4.98, 5.00, 1.0, 1.15, 'black')
# muebles de bano (no se ven con la puerta cerrada; sirven para la planta)
box('wc_tanque', 2.30, 2.70, 5.80, 6.00, 0, 0.75, 'quartz', 0.01)
cyl('wc_taza', 2.50, 5.60, 0, 0.40, 0.17, 'quartz')
box('regadera', 2.986, W, 5.30, 6.00, 0, 0.03, 'dark')

# ---- ventanal sur (ancho completo) ----
for i, x in enumerate([0, W / 3, 2 * W / 3, W]):
    box('ventanal_poste%d' % i, x - 0.02 if i else 0, x + 0.02 if i < 3 else W, -0.10, -0.05, 0, H, 'black')
box('ventanal_riel_inf', 0, W, -0.10, -0.05, 0, 0.04, 'black')
box('ventanal_riel_sup', 0, W, -0.10, -0.05, H - 0.05, H, 'black')
box('ventanal_vidrio', 0, W, -0.08, -0.072, 0, H, 'glass')
box('muro_sur_izq', -T, 0, -T, 0, 0, H, 'greige'); box('muro_sur_der', W, W + T, -T, 0, 0, H, 'conc')

# ---- patio ----
box('patio_piso', -1.5, W + 1.5, -3.6, -T, -0.1, -0.02, 'patio_floor')
box('patio_muro_fondo', -1.5, W + 1.5, -3.75, -3.6, 0, 3.0, 'patio_wall')
box('patio_muro_o', -1.65, -1.5, -3.75, 0, 0, 3.0, 'patio_wall'); box('patio_muro_e', W + 1.5, W + 1.65, -3.75, 0, 0, 3.0, 'patio_wall')
for px in (0.5, 1.9, 3.2):
    box('jardinera%.1f' % px, px - 0.3, px + 0.3, -3.55, -3.0, 0, 0.45, 'conc', 0.01)
    foliage('arbusto%.1f' % px, (px, -3.27, 1.0), (0.42, 0.3, 0.6), 700, 0.09)

# ---- plafon perimetral con luz indirecta ----
def soffit(n, x0, x1, y0, y1, lip, led):
    box('plafon_' + n, x0, x1, y0, y1, 2.55, 2.57, 'conc_ceil', coll=col_ceil)
    box('plafon_ceja_' + n, *lip, 2.57, 2.62, 'conc_ceil', coll=col_ceil)
    box('led_cornisa_' + n, *led, 2.572, 2.582, 'led', coll=col_ceil)
SW = 0.35
soffit('o', 0, SW, 0, L, (SW - 0.02, SW, 0, L), (SW - 0.10, SW - 0.08, 0.1, L - 0.1))
soffit('e', W - SW, W, 0, 4.80, (W - SW, W - SW + 0.02, 0, 4.80), (W - SW + 0.08, W - SW + 0.10, 0.1, 4.7))
soffit('s', SW, W - SW, 0, SW, (SW, W - SW, SW - 0.02, SW), (SW, W - SW, SW - 0.10, SW - 0.08))
soffit('n', 1.90, W - SW, 4.80 - SW, 4.80, (1.90, W - SW, 4.80 - SW, 4.80 - SW + 0.02), (1.95, W - SW, 4.80 - SW + 0.08, 4.80 - SW + 0.10))

# spots empotrados
for sx, sy in [(1.25, 0.9), (2.45, 0.9), (1.25, 2.3), (2.45, 2.3), (1.25, 3.7), (2.45, 3.7), (0.9, 5.4)]:
    c = cyl('spot_%.1f_%.1f' % (sx, sy), sx, sy, H - 0.004, H, 0.04, 'spot', 24)
    for cc in c.users_collection: cc.objects.unlink(c)
    col_ceil.objects.link(c)
    ld = bpy.data.lights.new('spotl', 'SPOT'); ld.energy = 130; ld.spot_size = math.radians(75); ld.spot_blend = 0.6
    ld.color = (1.0, 0.78, 0.55); ld.shadow_soft_size = 0.04
    lo = bpy.data.objects.new('spotl', ld); lo.location = (sx, sy, H - 0.02); col_main.objects.link(lo)

# ---- muro oeste: panel de listones de nogal detras del sillon ----
box('panel_fondo', 0, 0.012, 2.10, 4.00, 0, 2.55, 'dark')
y = 2.115
while y < 3.99:
    box('liston', 0.012, 0.040, y, y + 0.032, 0, 2.55, 'wal_z'); y += 0.06
box('led_listones', 0.045, 0.06, 2.10, 4.00, 2.535, 2.548, 'led_soft')

# ---- ARBOL: centro (0.30, 4.40) ----
box('arbol_maceta', 0.16, 0.44, 4.26, 4.54, 0, 0.42, 'conc', 0.012)
box('arbol_tierra', 0.18, 0.42, 4.28, 4.52, 0.38, 0.40, 'soil')
tube('arbol_tronco', [(0.30, 4.40, 0.40), (0.31, 4.41, 0.8), (0.28, 4.39, 1.2), (0.30, 4.40, 1.55)], 0.016, 'trunk')
tube('arbol_rama1', [(0.29, 4.39, 1.1), (0.38, 4.47, 1.4), (0.42, 4.52, 1.7)], 0.008, 'trunk')
tube('arbol_rama2', [(0.30, 4.40, 1.2), (0.24, 4.30, 1.5), (0.22, 4.26, 1.8)], 0.008, 'trunk')
foliage('arbol_hojas', (0.31, 4.40, 1.50), (0.27, 0.28, 0.48), 650, 0.075)

# ---- SILLON 2 PLAZAS: x 0-0.70, y 2.30-3.80 ----
box('sillon_base', 0.02, 0.70, 2.30, 3.80, 0.10, 0.26, 'fab_greige', 0.02, smooth=True)
box('sillon_respaldo', 0.0, 0.15, 2.30, 3.80, 0.10, 0.78, 'fab_greige', 0.03, smooth=True)
box('sillon_brazo_s', 0.0, 0.70, 2.30, 2.45, 0.10, 0.60, 'fab_greige', 0.03, smooth=True)
box('sillon_brazo_n', 0.0, 0.70, 3.65, 3.80, 0.10, 0.60, 'fab_greige', 0.03, smooth=True)
box('sillon_asiento_s', 0.15, 0.70, 2.455, 3.047, 0.26, 0.44, 'fab_greige', 0.04, smooth=True)
box('sillon_asiento_n', 0.15, 0.70, 3.053, 3.645, 0.26, 0.44, 'fab_greige', 0.04, smooth=True)
box('sillon_cojin_s', 0.15, 0.29, 2.455, 3.047, 0.44, 0.76, 'fab_greige', 0.04, smooth=True)
box('sillon_cojin_n', 0.15, 0.29, 3.053, 3.645, 0.44, 0.76, 'fab_greige', 0.04, smooth=True)
for lx in (0.06, 0.64):
    for ly in (2.36, 3.74):
        box('sillon_pata', lx - 0.02, lx + 0.02, ly - 0.02, ly + 0.02, 0, 0.10, 'black')

# ---- BASCULA: x 0-0.40, y 1.60-2.00 ----
box('bascula_base', 0.0, 0.40, 1.60, 2.00, 0, 0.06, 'black', 0.008)
box('bascula_plato', 0.03, 0.37, 1.72, 1.97, 0.06, 0.068, 'steel', 0.004)
box('bascula_columna', 0.17, 0.23, 1.62, 1.67, 0.06, 1.32, 'black', 0.004)
box('bascula_cabezal', 0.06, 0.34, 1.60, 1.69, 1.32, 1.40, 'black', 0.008)
box('bascula_display', 0.10, 0.30, 1.688, 1.692, 1.34, 1.385, 'screen')
box('bascula_estadimetro', 0.245, 0.26, 1.63, 1.645, 0.10, 2.00, 'steel')
box('bascula_tope', 0.245, 0.26, 1.645, 1.83, 1.985, 2.00, 'steel')

# ---- CAMILLA: x 0.70-2.60, y 0.45-1.15; cabecera x 0.70-0.95 ----
CZ = 0.62
box('camilla_colchon', 0.955, 2.60, 0.45, 1.15, CZ, CZ + 0.09, 'leather', 0.03, smooth=True)
hd = box('camilla_cabecera', 0.70, 0.945, 0.45, 1.15, CZ, CZ + 0.09, 'leather', 0.03, smooth=True)
# cabecera inclinada alrededor de la bisagra (x=0.95), sin salirse de la huella
hv = hd.data.vertices
for v in hv:
    dx = v.co.x - 0.945; z = v.co.z - CZ
    a = math.radians(-14)
    v.co.x = 0.945 + dx * math.cos(a) * 1.0 - z * 0.0
    v.co.z = CZ + z + (-dx) * math.sin(-a)
box('camilla_bastidor', 0.74, 2.56, 0.49, 1.11, CZ - 0.05, CZ, 'black')
for lx in (0.80, 2.50):
    for ly in (0.52, 1.08):
        box('camilla_pata', lx - 0.02, lx + 0.02, ly - 0.02, ly + 0.02, 0, CZ - 0.05, 'black')
box('camilla_travesano_o', 0.78, 0.82, 0.52, 1.08, 0.18, 0.22, 'black'); box('camilla_travesano_e', 2.48, 2.52, 0.52, 1.08, 0.18, 0.22, 'black')
box('camilla_larguero', 0.80, 2.50, 0.78, 0.82, 0.18, 0.22, 'black')

# ---- ESCRITORIO: x 2.20-2.75, y 3.20-4.80 (pegado al muro del bano) ----
box('escritorio_cubierta', 2.20, 2.75, 3.20, 4.80, 0.71, 0.75, 'wal_y', 0.003)
box('escritorio_costado', 2.20, 2.75, 3.20, 3.24, 0, 0.71, 'wal_z', 0.003)
box('escritorio_faldon', 2.20, 2.22, 3.24, 4.80, 0.12, 0.71, 'wal_z')
box('laptop', 2.36, 2.60, 3.86, 4.20, 0.75, 0.766, 'steel', 0.004)
cyl('lampara_base', 2.62, 4.62, 0.75, 0.765, 0.07, 'black'); cyl('lampara_poste', 2.62, 4.62, 0.765, 1.15, 0.008, 'black', 12)
box('lampara_brazo', 2.40, 2.63, 4.61, 4.63, 1.14, 1.155, 'black'); box('lampara_led', 2.41, 2.58, 4.612, 4.628, 1.137, 1.14, 'led_soft')
cyl('escritorio_maceta', 2.34, 4.55, 0.75, 0.86, 0.055, 'conc', 24, 0.065)
foliage('escritorio_planta', (2.34, 4.55, 0.95), (0.10, 0.10, 0.10), 160, 0.045)

# ---- SILLAS DE PACIENTE: 0.45 x 0.45 en x 1.50-1.95; y 3.20-3.65 y 3.95-4.40 (miran al este) ----
def silla_paciente(n, x0, y0):
    x1, y1 = x0 + 0.45, y0 + 0.45
    box(n + '_asiento', x0 + 0.02, x1, y0 + 0.02, y1 - 0.02, 0.38, 0.47, 'fab_dark', 0.03, smooth=True)
    box(n + '_respaldo', x0, x0 + 0.08, y0, y1, 0.36, 0.82, 'fab_dark', 0.03, smooth=True)
    box(n + '_brazo_s', x0, x1 - 0.10, y0, y0 + 0.05, 0.36, 0.64, 'fab_dark', 0.02, smooth=True)
    box(n + '_brazo_n', x0, x1 - 0.10, y1 - 0.05, y1, 0.36, 0.64, 'fab_dark', 0.02, smooth=True)
    for lx in (x0 + 0.04, x1 - 0.04):
        for ly in (y0 + 0.04, y1 - 0.04):
            cyl(n + '_pata', lx, ly, 0, 0.38, 0.012, 'wal_z', 12, 0.018)
silla_paciente('silla_pac_s', 1.50, 3.20); silla_paciente('silla_pac_n', 1.50, 3.95)

# ---- SILLA DEL MEDICO: x 2.90-3.38, y 3.56-4.04 (mira al oeste) ----
box('silla_med_asiento', 2.90, 3.36, 3.58, 4.02, 0.42, 0.50, 'leather', 0.03, smooth=True)
box('silla_med_respaldo', 3.30, 3.38, 3.56, 4.04, 0.46, 1.05, 'leather', 0.03, smooth=True)
cyl('silla_med_piston', 3.14, 3.80, 0.08, 0.42, 0.025, 'black', 16)
for k in range(5):
    a = k * 2 * math.pi / 5 + 0.3
    tube('silla_med_pie%d' % k, [(3.14, 3.80, 0.09), (3.14 + 0.12 * math.cos(a), 3.80 + 0.12 * math.sin(a), 0.075),
                                 (3.14 + 0.23 * math.cos(a), 3.80 + 0.23 * math.sin(a), 0.055)], 0.014, 'black')
    cyl('silla_med_rueda%d' % k, 3.14 + 0.23 * math.cos(a), 3.80 + 0.23 * math.sin(a), 0, 0.05, 0.022, 'black', 12)

# ---- TV: x 3.566-3.686 (incluye soporte), y 2.35-3.05 ----
box('tv_soporte', 3.626, W, 2.60, 2.80, 1.42, 1.58, 'black')
box('tv', 3.596, 3.626, 2.35, 3.05, 1.30, 1.70, 'black', 0.003)
box('tv_pantalla', 3.5955, 3.597, 2.358, 3.042, 1.308, 1.692, 'screen')

# ---- BARRA CON TARJA: x 3.186-3.686, y 0.15-1.85; divisiones y 0.40 y 1.45; tarja x 3.241-3.631, y 0.60-1.10 ----
BX0, BY0, BY1, BH = 3.186, 0.15, 1.85, 0.90
box('barra_zoclo', BX0 + 0.06, W, BY0 + 0.02, BY1 - 0.02, 0, 0.10, 'dark')
box('barra_fondo', BX0 + 0.019, BX0 + 0.03, BY0, BY1, 0.10, BH - 0.02, 'dark')
box('barra_costado_s', BX0, W, BY0, BY0 + 0.018, 0.10, BH - 0.02, 'wal_z'); box('barra_costado_n', BX0, W, BY1 - 0.018, BY1, 0.10, BH - 0.02, 'wal_z')
g = 0.0015
def frente(n, y0, y1, z0, z1): box('barra_frente_' + n, BX0, BX0 + 0.018, y0 + g, y1 - g, z0 + g, z1 - g, 'wal_z')
frente('puerta_s', BY0 + 0.018, 0.40, 0.10, BH - 0.02)
frente('puerta_c1', 0.40, 0.925, 0.10, BH - 0.02); frente('puerta_c2', 0.925, 1.45, 0.10, BH - 0.02)
for k in range(3): frente('cajon%d' % k, 1.45, BY1 - 0.018, 0.10 + k * 0.26, 0.10 + (k + 1) * 0.26)
# cubierta de cuarzo con hueco para tarja
CX0 = BX0 - 0.01; cz0, cz1 = BH - 0.02, BH
box('cubierta_s', CX0, W, BY0, 0.60, cz0, cz1, 'quartz'); box('cubierta_n', CX0, W, 1.10, BY1, cz0, cz1, 'quartz')
box('cubierta_o', CX0, 3.241, 0.60, 1.10, cz0, cz1, 'quartz'); box('cubierta_e', 3.631, W, 0.60, 1.10, cz0, cz1, 'quartz')
box('tarja_fondo', 3.241, 3.631, 0.60, 1.10, 0.70, 0.705, 'steel')
box('tarja_o', 3.236, 3.241, 0.60, 1.10, 0.70, cz0, 'steel'); box('tarja_e', 3.631, 3.636, 0.60, 1.10, 0.70, cz0, 'steel')
box('tarja_s', 3.236, 3.636, 0.595, 0.60, 0.70, cz0, 'steel'); box('tarja_n', 3.236, 3.636, 1.10, 1.105, 0.70, cz0, 'steel')
cyl('tarja_desague', 3.436, 0.85, 0.705, 0.707, 0.025, 'black', 20)
cyl('grifo_base', 3.655, 0.85, BH, BH + 0.03, 0.022, 'black', 20)
tube('grifo', [(3.655, 0.85, BH), (3.655, 0.85, 1.20), (3.64, 0.85, 1.27), (3.57, 0.85, 1.30), (3.50, 0.85, 1.27), (3.485, 0.85, 1.19)], 0.011, 'black')
box('grifo_palanca', 3.62, 3.66, 0.80, 0.812, BH + 0.04, BH + 0.05, 'black')
cyl('jabon', 3.52, 1.28, BH, BH + 0.14, 0.03, 'amber', 20); cyl('jabon_bomba', 3.52, 1.28, BH + 0.14, BH + 0.19, 0.008, 'black', 10)
cyl('barra_maceta', 3.50, 1.62, BH, BH + 0.11, 0.06, 'dark', 24, 0.07); foliage('barra_planta', (3.50, 1.62, BH + 0.20), (0.11, 0.11, 0.10), 170, 0.045)
# mueble superior: modulos cerrados (norte) + nicho abierto con LED
UX0, UZ0, UZ1 = W - 0.32, 1.45, 2.05
box('sup_cerrado', UX0 + 0.02, W, 1.25, BY1, UZ0, UZ1, 'dark')
box('sup_cerrado_costados', UX0, W, 1.25, 1.268, UZ0, UZ1, 'wal_z'); box('sup_cerrado_costado_n', UX0, W, BY1 - 0.018, BY1, UZ0, UZ1, 'wal_z')
box('sup_puerta1', UX0, UX0 + 0.018, 1.268 + g, 1.55 - g, UZ0 + g, UZ1 - g, 'wal_z'); box('sup_puerta2', UX0, UX0 + 0.018, 1.55 + g, BY1 - 0.018 - g, UZ0 + g, UZ1 - g, 'wal_z')
box('sup_repisa_inf', UX0, W, BY0, 1.25, UZ0, UZ0 + 0.03, 'wal_y'); box('sup_repisa_sup', UX0, W, BY0, 1.25, UZ1 - 0.03, UZ1, 'wal_y')
box('sup_costado_s', UX0, W, BY0, BY0 + 0.03, UZ0, UZ1, 'wal_z')
box('led_bajo_repisa', W - 0.06, W - 0.045, BY0 + 0.05, BY1 - 0.05, UZ0 - 0.008, UZ0, 'led')
box('led_nicho', W - 0.06, W - 0.045, BY0 + 0.05, 1.24, UZ1 - 0.038, UZ1 - 0.03, 'led')
yb = 0.48
for k in range(7):
    w = random.uniform(0.022, 0.045); h = random.uniform(0.20, 0.27)
    box('libro%d' % k, W - 0.24, W - 0.06, yb, yb + w, UZ0 + 0.03, UZ0 + 0.03 + h, random.choice(BOOKS)); yb += w + 0.002
cyl('nicho_maceta', W - 0.16, 1.02, UZ0 + 0.03, UZ0 + 0.13, 0.05, 'conc', 24, 0.06); foliage('nicho_planta', (W - 0.16, 1.02, UZ0 + 0.22), (0.10, 0.11, 0.10), 150, 0.045)

# ---- cuadro abstracto sobre el muro del bano ----
box('cuadro_marco', 2.95, 3.55, 4.775, 4.80, 1.25, 2.05, 'black')
box('cuadro_fondo', 2.97, 3.53, 4.772, 4.776, 1.27, 2.03, flat('lienzo', (0.55, 0.50, 0.42), 0.9))
box('cuadro_mancha1', 3.02, 3.30, 4.770, 4.773, 1.55, 1.95, flat('lienzo_n', (0.02, 0.02, 0.02), 0.9))
box('cuadro_mancha2', 3.22, 3.48, 4.768, 4.771, 1.33, 1.70, flat('lienzo_c', (0.16, 0.085, 0.04), 0.9))
box('cuadro_mancha3', 3.06, 3.20, 4.769, 4.772, 1.36, 1.50, flat('lienzo_g', (0.25, 0.25, 0.24), 0.9))

# ---------------- luz natural ----------------
w = bpy.data.worlds.new('w'); scene.world = w; w.use_nodes = True
bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.75, 0.85, 1.0, 1); bg.inputs['Strength'].default_value = 1.6
sd = bpy.data.lights.new('sol', 'SUN'); sd.energy = 2.2; sd.angle = math.radians(2); sd.color = (1.0, 0.93, 0.82)
so = bpy.data.objects.new('sol', sd); so.rotation_euler = (math.radians(38), 0, math.radians(-158)); col_main.objects.link(so)

# ---------------- render ----------------
scene.render.engine = 'CYCLES'
scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8; scene.cycles.diffuse_bounces = 5
scene.cycles.sample_clamp_indirect = 8
scene.view_settings.view_transform = 'AgX'
try: scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception: pass
scene.render.image_settings.file_format = 'PNG'

def cam(name, loc, target, lens, shift_y=0.0, ortho=None, aspect=1.5, exposure=0.0, hide_ceiling=False):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.sensor_width = 36; cd.shift_y = shift_y
    cd.clip_start = 0.02
    if ortho: cd.type = 'ORTHO'; cd.ortho_scale = ortho
    o = bpy.data.objects.new(name, cd); o.location = loc; col_main.objects.link(o)
    d = Vector(target) - Vector(loc); o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return dict(obj=o, aspect=aspect, exposure=exposure, hide=hide_ceiling, name=name)

CAMS = [
    cam('1_desde_entrada', (1.05, 4.86, 1.50), (2.05, 0.60, 1.50), 14, shift_y=-0.10, exposure=0.5),
    cam('2_desde_ventanal', (3.05, 0.20, 1.55), (0.55, 4.50, 1.55), 14, shift_y=-0.10, exposure=0.8),
    cam('3_escritorio', (0.40, 2.05, 1.45), (2.90, 4.40, 1.45), 16, shift_y=-0.08, exposure=0.8),
    cam('4_barra_tarja', (1.15, 2.75, 1.35), (3.60, 0.95, 1.35), 21, shift_y=-0.05, exposure=0.7),
    cam('0_planta', (W / 2, L / 2, 9.0), (W / 2, L / 2, 0), 50, ortho=6.5, aspect=4.0 / 6.5, exposure=0.6, hide_ceiling=True),
]
for c in CAMS:
    if ONLY and not any(c['name'].startswith(k) for k in ONLY): continue
    scene.camera = c['obj']
    extra = [o for o in bpy.data.objects if o.name.startswith(('nicho_', 'sup_', 'libro'))]
    for o in list(col_ceil.objects) + HIDE_IN_PLAN + extra: o.hide_render = c['hide']
    if c['obj'].data.type == 'ORTHO':
        scene.render.resolution_y = RESX; scene.render.resolution_x = int(RESX * c['aspect'])
    else:
        scene.render.resolution_x = RESX; scene.render.resolution_y = int(RESX / c['aspect'])
    scene.view_settings.exposure = c['exposure']
    scene.render.filepath = '%s/%s.png' % (OUT, c['name'])
    bpy.ops.render.render(write_still=True)
    print('RENDER OK', c['name'], flush=True)
