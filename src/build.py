#!/usr/bin/env python3
# Genera site/ del directorio de autoescuelas (Valencia + Canarias + Madrid)
# y copia el HTML a la raíz, que es lo que publica GitHub Pages.
import csv, html, json, os, posixpath, re, shutil, sys

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
    '<a href="madrid.html">Madrid</a>'
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

def madrid_rows(items):
    """Adapta el dataset de Madrid al listado. El % DGT solo se muestra si viene verificado."""
    rows = []
    for r in items:
        direccion = r["direccion"]
        mun = (r.get("municipio") or "").strip()
        if mun and mun not in direccion:
            direccion = f"{direccion}, {mun}"
        verificado = (
            r.get("aprobados_dgt_estado") == "VERIFICADO"
            and r.get("aprobados_dgt_porcentaje") is not None
        )
        rows.append({
            "nombre": r["nombre"],
            "direccion": direccion,
            "cp": r.get("codigo_postal") or "",
            "web": r.get("fuente_url") or "",
            "telefono": r.get("telefono") or "sin datos",
            "espera_practicas": "sin datos",
            "fuente_espera": "",
            "fuente": r.get("fuente_url") or "",
            "aprobados_practico_B": str(r["aprobados_dgt_porcentaje"]) if verificado else "sin datos",
            "periodo_dgt": "",
            "fuente_dgt": "",
        })
    return rows

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
mad_src = json.load(open(os.path.join(D, "data/autoescuelas_madrid.json"), encoding="utf-8"))
mad = madrid_rows(mad_src)

# --- index hub ---
page(
    "index.html",
    "Directorio de autoescuelas (España)",
    f"""
<p>Listados con datos públicos citados: dirección, teléfono (si hay) y web (si hay). En Valencia y Canarias, si el código de autoescuela está asociado, también figuran los aprobados del práctico B según microdatos DGT (10/2025–09/2026). En la selección de Madrid esos porcentajes están sin datos.</p>
<ul class="provincias">
<li><a href="valencia.html"><b>Valencia</b></a> — {len(val)} autoescuelas · <a href="centros-examen.html">centros de examen</a></li>
<li><a href="canarias.html"><b>Canarias</b></a>
  <ul>
  <li><a href="las-palmas.html">Las Palmas de Gran Canaria</a> — {len(lp)} sedes</li>
  <li><a href="santa-cruz-de-tenerife.html">Santa Cruz de Tenerife</a> — {len(tf)} sedes</li>
  <li><a href="centros-examen-canarias.html">centros de examen Canarias</a></li>
  </ul>
</li>
<li><a href="madrid.html"><b>Madrid</b></a> — selección parcial de {len(mad)} sedes verificadas, no un directorio exhaustivo · aprobados DGT sin datos</li>
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

# --- Madrid: selección parcial, sin % DGT ---
page(
    "madrid.html",
    "Autoescuelas en Madrid",
    f"""
<p class="nota">Selección parcial de {len(mad)} sedes de la provincia de Madrid, no un directorio exhaustivo ni un ranking. Nombre, domicilio y teléfono salen de la web oficial de cada centro (consulta del 8 de noviembre de 2026): tres en Madrid capital y una en Alcalá de Henares (GALA San Vidal, calle San Vidal 13; no es una sede en la calle Alcalá). Hay muchas más autoescuelas en la provincia que no figuran aquí. El orden de la tabla no es un ranking.</p>
<p>Aprobados del práctico B y códigos de autorización de la DGT: <b>sin datos</b>. No están verificados para estas fichas y no se copian porcentajes de otras provincias. Tiempos de espera: sin datos. No mostramos precios. Centros de examen de Madrid: sin datos en esta página.</p>
<p>Madrid capital: GALA Clara del Rey, GALA Goya y Lara Plaza Elíptica. Alcalá de Henares: GALA San Vidal.</p>
{school_table(mad)}
<p>Guías del directorio: <a href="como-elegir.html">cómo elegir si hay lista de espera</a> · <a href="adelantar-examen.html">¿se puede adelantar el examen pagando?</a></p>
<p><a href="index.html">Volver al directorio de España</a></p>
""",
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

# GitHub Pages publica la raíz de main en /autoescuelas-valencia/
ROOT = os.path.dirname(D)
for fname in os.listdir(OUT):
    if fname.endswith(".html"):
        shutil.copyfile(os.path.join(OUT, fname), os.path.join(ROOT, fname))

BASE = "/autoescuelas-valencia/"
ok = True

def report(status, name, detail=""):
    global ok
    if status == "FALLA":
        ok = False
    line = f"{status} {name}"
    if detail:
        line += f" — {detail}"
    print(line)

rotos = []
for f in sorted(os.listdir(OUT)):
    if not f.endswith(".html"):
        continue
    text = open(os.path.join(OUT, f), encoding="utf-8").read()
    for h in re.findall(r'href="([^"]+)"', text):
        if h.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if h.startswith("/") or h.startswith("../") or "\\" in h:
            rotos.append(f"{f} -> {h}")
            continue
        resolved = posixpath.normpath(BASE + h)
        rel = resolved[len(BASE):] if resolved.startswith(BASE) else ""
        if not rel or not os.path.exists(os.path.join(OUT, rel)):
            rotos.append(f"{f} -> {h} => {resolved}")
if rotos:
    for item in rotos:
        report("FALLA", "enlace_interno", item)
else:
    report("PASA", "enlaces_internos_relativos", f"resuelven bajo {BASE}")

mad_html = open(os.path.join(OUT, "madrid.html"), encoding="utf-8").read()
idx_html = open(os.path.join(OUT, "index.html"), encoding="utf-8").read()
val_html = open(os.path.join(OUT, "valencia.html"), encoding="utf-8").read()
can_html = open(os.path.join(OUT, "canarias.html"), encoding="utf-8").read()
lp_html = open(os.path.join(OUT, "las-palmas.html"), encoding="utf-8").read()
tf_html = open(os.path.join(OUT, "santa-cruz-de-tenerife.html"), encoding="utf-8").read()

report("PASA" if len(mad_src) == 4 else "FALLA", "dataset_4_sedes", str(len(mad_src)))
report(
    "PASA" if all(r.get("aprobados_dgt_porcentaje") is None and r.get("aprobados_dgt_estado") == "NO VERIFICADO" for r in mad_src) else "FALLA",
    "dataset_dgt_no_verificado",
)
esperados = [
    "GALA Clara del Rey", "Calle Clara del Rey, 81", "28002", "671415691",
    "https://autoescuelagala.com/autoescuela-clara-del-rey/",
    "GALA Goya", "Calle de Goya, 108", "28009", "615946629",
    "https://autoescuelagala.com/autoescuela-goya/",
    "GALA San Vidal", "Calle San Vidal, 13", "Alcalá de Henares", "28803", "617978359",
    "https://autoescuelagala.com/autoescuela-alcala/",
    "Lara Plaza Elíptica", "Avenida Oporto, 4", "28019", "914601022 / 658362510",
    "https://autoescuelalara.com/tiendas/plaza-eliptica/",
    "Selección parcial", "no un directorio exhaustivo", "sin datos",
]
faltan = [s for s in esperados if s not in mad_html]
report("PASA" if not faltan else "FALLA", "madrid_ficha", ", ".join(faltan) if faltan else "4 sedes y aviso de selección parcial")
cuerpo = mad_html.split("</style>", 1)[-1]
report("PASA" if not re.search(r"\d+(?:[.,]\d+)?\s*%", cuerpo) else "FALLA", "madrid_sin_porcentaje_numerico")
report("PASA" if cuerpo.count(">sin datos</td><td>sin datos</td>") == 4 else "FALLA", "madrid_filas_sin_datos_dgt", str(cuerpo.count(">sin datos</td><td>sin datos</td>")))
report("PASA" if "matraba-listados" not in mad_html else "FALLA", "madrid_sin_enlace_microdatos")
report("PASA" if "mejores" not in mad_html.lower() else "FALLA", "madrid_sin_ranking_mejores")
report("PASA" if "autoescuela-moncloa" not in mad_html and "autoescuela-pelayo" not in mad_html else "FALLA", "madrid_sin_sedes_excluidas")
report("PASA" if 'href="madrid.html"' in idx_html and "aprobados DGT sin datos" in idx_html else "FALLA", "hub_enlace_madrid")
report("PASA" if val_html.count("<tr><td>") == 22 and "51.2% (268/523)" in val_html else "FALLA", "valencia_conservada")
report("PASA" if "Primera ampliación fuera de Valencia" in can_html and "30 sedes" in lp_html and "20 sedes" in tf_html else "FALLA", "canarias_conservada")
report("PASA" if "Ingresos de este proyecto: no se inventan cifras aquí." in idx_html else "FALLA", "nota_ingresos_sin_cifras")
copias_ok = all(
    open(os.path.join(OUT, f), encoding="utf-8").read() == open(os.path.join(ROOT, f), encoding="utf-8").read()
    for f in os.listdir(OUT) if f.endswith(".html")
)
report("PASA" if copias_ok and os.path.exists(os.path.join(ROOT, "madrid.html")) else "FALLA", "copia_raiz_github_pages")
hay_sitemap = os.path.exists(os.path.join(ROOT, "sitemap.xml")) or os.path.exists(os.path.join(OUT, "sitemap.xml"))
report("FALLA" if hay_sitemap else "PASA", "sitemap_ausente_sin_cambio", "no se crea sitemap.xml")
print("NO VERIFICADO porcentajes_dgt_madrid — porcentaje null y estado NO VERIFICADO; la página muestra sin datos y no calcula microdatos")
print("NO VERIFICADO codigos_autorizacion_madrid — no vienen en el dataset")
print("NO VERIFICADO centros_examen_madrid — sin ficha verificada en esta ampliación")
print("NO VERIFICADO ruta_publica_http — no se fusiona ni se despliega; ruta esperada https://marcosrodmart-hub.github.io/autoescuelas-valencia/madrid.html")
print(
    "valencia", len(val),
    "las_palmas", len(lp),
    "tenerife", len(tf),
    "madrid", len(mad),
    "paginas", sorted(os.listdir(OUT)),
    "enlaces_internos_ok", ok,
)
sys.exit(0 if ok else 1)
