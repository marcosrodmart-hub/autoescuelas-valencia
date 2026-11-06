#!/usr/bin/env python3
# Genera site/ del directorio de autoescuelas (Valencia + Canarias)
import csv, html, json, os, re, sys

D = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(D, "site")
os.makedirs(OUT, exist_ok=True)
e = html.escape

CSS = (
    "body{font-family:sans-serif;max-width:860px;margin:auto;padding:1em;line-height:1.5}"
    "table{border-collapse:collapse;width:100%;font-size:.9em}td,th{border:1px solid #ccc;padding:4px}"
    "nav a{margin-right:1em}.nota{background:#fff7d6;padding:.6em}"
    "ul.provincias{line-height:1.8}"
)
NAV = (
    '<nav>'
    '<a href="index.html">Inicio</a>'
    '<a href="valencia.html">Valencia</a>'
    '<a href="canarias.html">Canarias</a>'
    '<a href="como-elegir.html">Cómo elegir</a>'
    '<a href="adelantar-examen.html">¿Adelantar examen?</a>'
    '<a href="centros-examen.html">Centros Valencia</a>'
    '<a href="centros-examen-canarias.html">Centros Canarias</a>'
    '</nav>'
)
FD = "https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/conductores-autoescuelas.html"
FOOT = (
    '<hr><p><small>Datos de fuentes públicas citadas (microdatos DGT y directorios citados por fila). '
    'No mostramos precios. Tasa DGT 2.1 de examen: 94,05 € '
    '(<a href="https://sede.dgt.gob.es/es/permisos-de-conducir/obtencion-y-gestion-de-permisos/solicitud-de-prueba-de-aptitud-de-examen/index.html">sede DGT</a>).</small></p>'
)

def page(fname, title, body):
    open(os.path.join(OUT, fname), "w", encoding="utf-8").write(
        f'<!doctype html><html lang="es"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width">'
        f'<title>{e(title)}</title><style>{CSS}</style></head>'
        f'<body>{NAV}<h1>{e(title)}</h1>{body}{FOOT}</body></html>'
    )

def load_csv(name):
    p = os.path.join(D, "data", name)
    return list(csv.DictReader(open(p, encoding="utf-8")))

def lk(u, t=None):
    return f'<a href="{e(u)}" rel="nofollow">{e(t or u)}</a>' if u else "—"

def table_rows(rows):
    out = []
    for r in rows:
        espera = e(r.get("espera_practicas") or "sin datos")
        if r.get("fuente_espera"):
            espera += f' ({lk(r["fuente_espera"], "fuente")})'
        aprob = e(r.get("aprobados_practico_B") or "sin datos")
        if r.get("fuente_dgt"):
            aprob += f' · {e(r.get("periodo_dgt") or "")} · {lk(r["fuente_dgt"], "DGT")}'
        out.append(
            "<tr>"
            f"<td>{e(r['nombre'])}</td>"
            f"<td>{e(r['direccion'])}{(', '+e(r['cp'])) if r.get('cp') else ''}</td>"
            f"<td>{lk(r.get('web') or '', 'web')}</td>"
            f"<td>{e(r.get('telefono') or 'sin datos')}</td>"
            f"<td>{espera}</td>"
            f"<td>{aprob}</td>"
            f"<td>{lk(r.get('fuente') or '', 'fuente')}</td>"
            "</tr>"
        )
    return "".join(out)

def school_table(rows):
    return (
        "<table><tr><th>Nombre</th><th>Dirección</th><th>Web</th><th>Teléfono</th>"
        "<th>Espera prácticas/examen</th><th>Aprobados práctico B (DGT)</th><th>Fuente</th></tr>"
        f"{table_rows(rows)}</table>"
    )

def nota_esperas():
    return (
        '<p class="nota">Aún no tenemos datos verificados de tiempos de espera para prácticas o examen. '
        "No mostramos precios. Aprobados: % de aptos en la prueba de circulación del permiso B, "
        "todas las secciones del código DGT, 10/2025–09/2026, microdatos oficiales DGT. "
        "Asociación nombre→código DGT hecha por código de autoescuela.</p>"
    )

# --- data ---
val = load_csv("autoescuelas_valencia.csv")
lp = load_csv("autoescuelas_las_palmas.csv")
tf = load_csv("autoescuelas_santa_cruz_de_tenerife.csv")

# --- index hub ---
page(
    "index.html",
    "Directorio de autoescuelas (España)",
    f"""
<p>Listados con datos públicos citados: dirección, teléfono (si hay), web (si hay) y aprobados del práctico B según microdatos DGT (10/2025–09/2026).</p>
<ul class="provincias">
<li><a href="valencia.html"><b>Valencia</b></a> — {len(val)} autoescuelas · <a href="centros-examen.html">centros de examen</a></li>
<li><a href="canarias.html"><b>Canarias</b></a>
  <ul>
  <li><a href="las-palmas.html">Las Palmas de Gran Canaria</a> — {len(lp)} sedes</li>
  <li><a href="santa-cruz-de-tenerife.html">Santa Cruz de Tenerife</a> — {len(tf)} sedes</li>
  <li><a href="centros-examen-canarias.html">centros de examen Canarias</a></li>
  </ul>
</li>
</ul>
<p>Guías: <a href="como-elegir.html">cómo elegir si hay lista de espera</a> · <a href="adelantar-examen.html">¿se puede adelantar el examen pagando?</a></p>
<p class="nota">Ingresos de este proyecto: no se inventan cifras aquí. Ver chat con el dueño.</p>
""",
)

# --- Valencia (antes index) ---
page(
    "valencia.html",
    "Autoescuelas en Valencia ciudad",
    f'{nota_esperas()}<p>{len(val)} autoescuelas. Ver también los <a href="centros-examen.html">aprobados por centro de examen</a>.</p>{school_table(val)}',
)

# --- Canarias hub + provinces ---
page(
    "canarias.html",
    "Autoescuelas en Canarias",
    f"""
<p>Primera ampliación fuera de Valencia: capitales de <b>Las Palmas</b> y <b>Santa Cruz de Tenerife</b>. Direcciones y fichas citadas desde directorios públicos; aprobados desde microdatos DGT 10/2025–09/2026.</p>
<ul class="provincias">
<li><a href="las-palmas.html"><b>Las Palmas de Gran Canaria</b></a> — {len(lp)} sedes listadas</li>
<li><a href="santa-cruz-de-tenerife.html"><b>Santa Cruz de Tenerife</b></a> — {len(tf)} sedes listadas</li>
<li><a href="centros-examen-canarias.html">Centros de examen DGT en Canarias</a></li>
</ul>
{nota_esperas()}
""",
)

page(
    "las-palmas.html",
    "Autoescuelas en Las Palmas de Gran Canaria",
    f'{nota_esperas()}<p>{len(lp)} sedes. Provincia Las Palmas. Volver a <a href="canarias.html">Canarias</a>.</p>{school_table(lp)}',
)

page(
    "santa-cruz-de-tenerife.html",
    "Autoescuelas en Santa Cruz de Tenerife",
    f'{nota_esperas()}<p>{len(tf)} sedes. Provincia Santa Cruz de Tenerife. Volver a <a href="canarias.html">Canarias</a>.</p>{school_table(tf)}',
)

# --- guías (igual que antes) ---
page(
    "como-elegir.html",
    "Cómo elegir autoescuela si hay lista de espera",
    """
<p>Mucha gente se queja de esperas largas: <a href="https://www.reddit.com/r/valencia/comments/1syr0j0/es_normal_que_una_autoescuela_te_haga_esperar/">Reddit r/valencia</a>, <a href="https://www.reddit.com/r/askspain/comments/1p8c0f0/retraso_intencionado_de_autoescuela_sospecha_de/">7 meses esperando (r/askspain)</a>, <a href="https://www.lasexta.com/motor/noticias/carnet-conducir-sigue-atascado-faltan-solo-examinadores-sobran-solo-alumnos_202610066ac4da3fa4297764c3aac2ae.html">La Sexta</a>.</p>
<ol>
<li><b>Pregunta por escrito</b> cuánto tardan hoy en dar la primera práctica y cuántos alumnos presentan a examen por ciclo.</li>
<li><b>Entiende el reparto:</b> la DGT asigna los huecos de examen a cada autoescuela con el sistema CAPA, según sus alumnos pendientes y con un factor corrector por porcentaje de aprobados (<a href="https://revista.dgt.es/es/reportajes/2021/01ENERO/0114-CAPA-prueba.shtml">Revista DGT</a>, <a href="https://www.cnmc.es/sites/default/files/5791040.pdf">CNMC</a>). Un buen índice de aprobados ayuda a la autoescuela a recibir más plazas.</li>
<li><b>Mira los aprobados públicos</b> por autoescuela (datos DGT).</li>
<li><b>Desconfía de “packs”</b> que te obligan a pagar muchas clases por adelantado y pide el desglose.</li>
<li><b>La tasa DGT es fija:</b> 94,05 € (tasa 2.1), con dos convocatorias (<a href="https://sede.dgt.gob.es/es/permisos-de-conducir/obtencion-y-gestion-de-permisos/solicitud-de-prueba-de-aptitud-de-examen/index.html">sede DGT</a>).</li>
</ol>
""",
)

page(
    "adelantar-examen.html",
    "¿Pueden adelantarte el examen pagando? Lo que dice la DGT",
    """
<p>Las fechas de examen práctico no se venden. Las gestiona la DGT y las solicita la autoescuela: “si te presentas a través de una autoescuela, será la propia escuela la que se encargue de presentar tu solicitud” (<a href="https://www.dgt.es/nuestros-servicios/permisos-de-conducir/obtener-un-nuevo-permiso-de-conducir/requisitos-preparacion-y-presentacion-a-examen/index.html">DGT</a>).</p>
<p>Cada Jefatura reparte su capacidad en ciclos de 5 a 15 días hábiles entre las autoescuelas según sus alumnos pendientes y su tasa de aprobados (sistema CAPA, Anexo IX del Reglamento General de Conductores): <a href="https://revista.dgt.es/es/reportajes/2021/01ENERO/0114-CAPA-prueba.shtml">Revista DGT</a>, <a href="https://www.cnmc.es/sites/default/files/5791040.pdf">informe CNMC</a>.</p>
<p>Lo único que pagas a la DGT es la tasa 2.1 de 94,05 € (<a href="https://sede.dgt.gob.es/es/permisos-de-conducir/obtencion-y-gestion-de-permisos/solicitud-de-prueba-de-aptitud-de-examen/index.html">sede DGT</a>). Ningún pago oficial adelanta tu turno. Lo que una autoescuela decida sobre a qué alumnos presenta dentro de su cupo depende de ella: pide que te expliquen su criterio por escrito.</p>
""",
)

# --- centros examen Valencia ---
C = json.load(open(os.path.join(D, "data/centros_examen_valencia.json"), encoding="utf-8"))
M = {}
for k, v in C.items():
    n = "Valencia (ciudad)" if k.startswith("Valencia") else k
    for t, a in v.items():
        b = M.setdefault(n, {}).setdefault(t, [0, 0, 0])
        b[0] += a[0]; b[1] += a[1]; b[2] += a[2]

def pc(a):
    if a and a[0] + a[1]:
        return f"{100 * a[0] / (a[0] + a[1]):.1f}% ({a[0]:,}/{a[0] + a[1]:,})".replace(",", ".")
    return "sin datos"

trc = "".join(
    f"<tr><td>{e(n)}</td><td>{pc(v.get('teorico'))}</td><td>{pc(v.get('practico'))}</td></tr>"
    for n, v in sorted(M.items(), key=lambda x: -sum(x[1].get("practico", [0, 0])[:2]))
)
page(
    "centros-examen.html",
    "Centros de examen DGT en la provincia de Valencia: aprobados del permiso B",
    f"""
<p>Porcentaje de aptos en el examen teórico y en el práctico (prueba de conducción y circulación) del permiso B en cada centro de examen de la provincia de Valencia, sumando octubre de 2025 a septiembre de 2026. Fuente: microdatos oficiales de la DGT (<a href="{FD}">DGT, listados de autoescuelas</a>). Entre paréntesis, aptos / exámenes realizados.</p>
<table><tr><th>Centro de examen</th><th>Teórico B</th><th>Práctico B</th></tr>{trc}</table>
<p class="nota">Lo que estos datos no dicen: tiempos de espera para examen (sin datos), direcciones y horarios de cada centro (sin datos verificados aquí; consulta la <a href="https://www.dgt.es/">web oficial de la DGT</a>). Un porcentaje alto o bajo no implica que un centro sea más fácil.</p>
<p>Normalmente no eliges centro: la solicitud la tramita tu autoescuela ante la DGT. Ver también <a href="adelantar-examen.html">si se puede adelantar el examen pagando</a> y el <a href="valencia.html">listado de autoescuelas de Valencia</a>.</p>
""",
)

# --- centros Canarias ---
def centros_table(path):
    data = json.load(open(os.path.join(D, "data", path), encoding="utf-8"))
    rows = "".join(
        f"<tr><td>{e(n)}</td><td>{pc(v.get('teorico'))}</td><td>{pc(v.get('practico'))}</td></tr>"
        for n, v in sorted(data.items(), key=lambda x: -sum(x[1].get("practico", [0, 0])[:2]))
    )
    return f"<table><tr><th>Centro de examen</th><th>Teórico B</th><th>Práctico B</th></tr>{rows}</table>"

page(
    "centros-examen-canarias.html",
    "Centros de examen DGT en Canarias: aprobados del permiso B",
    f"""
<p>Aptos en teórico y práctico B (circulación), octubre 2025–septiembre 2026, por centro de examen en las provincias de Las Palmas y Santa Cruz de Tenerife. Fuente: microdatos DGT (<a href="{FD}">DGT</a>).</p>
<h2>Provincia de Las Palmas</h2>
{centros_table("centros_examen_las_palmas.json")}
<h2>Provincia de Santa Cruz de Tenerife</h2>
{centros_table("centros_examen_santa_cruz_de_tenerife.json")}
<p class="nota">Incluye centros en islas (p. ej. Arrecife, La Palma, La Gomera, El Hierro) porque figuran en los microdatos de esas provincias. Tiempos de espera: sin datos. Direcciones de centros: sin datos verificados aquí.</p>
<p><a href="canarias.html">Volver a Canarias</a> · <a href="las-palmas.html">Las Palmas</a> · <a href="santa-cruz-de-tenerife.html">Santa Cruz de Tenerife</a></p>
""",
)

# redirect-compatible: keep old index content accessible — already have valencia.html
# Also write a thin alias note: old bookmarks to index now see hub (OK)

# verify internal links
ok = True
for f in os.listdir(OUT):
    if not f.endswith(".html"):
        continue
    for h in re.findall(r'href="([^"]+)"', open(os.path.join(OUT, f), encoding="utf-8").read()):
        if not h.startswith("http") and not h.startswith("#") and not os.path.exists(os.path.join(OUT, h)):
            print("ROTO", f, h)
            ok = False
print(
    "valencia", len(val),
    "las_palmas", len(lp),
    "tenerife", len(tf),
    "paginas", sorted(os.listdir(OUT)),
    "enlaces_internos_ok", ok,
)
sys.exit(0 if ok else 1)
