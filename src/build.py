import csv, html, os, re, sys
D=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(D,"site"); os.makedirs(OUT,exist_ok=True)
e=html.escape
CSS="body{font-family:sans-serif;max-width:860px;margin:auto;padding:1em;line-height:1.5}table{border-collapse:collapse;width:100%;font-size:.9em}td,th{border:1px solid #ccc;padding:4px}nav a{margin-right:1em}.nota{background:#fff7d6;padding:.6em}"
NAV='<nav><a href="index.html">Autoescuelas Valencia</a><a href="como-elegir.html">Cómo elegir con lista de espera</a><a href="adelantar-examen.html">¿Adelantar el examen pagando?</a><a href="centros-examen.html">Centros de examen</a></nav>'
def page(f,t,body):
    open(os.path.join(OUT,f),"w").write(f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{e(t)}</title><style>{CSS}</style></head><body>{NAV}<h1>{e(t)}</h1>{body}<hr><p><small>Borrador local, no publicado. Datos de fuentes públicas citadas.</small></p></body></html>')
rows=list(csv.DictReader(open(os.path.join(D,"data/autoescuelas_valencia.csv"))))
lk=lambda u,t=None:f'<a href="{e(u)}" rel="nofollow">{e(t or u)}</a>' if u else "—"
tr="".join(f"<tr><td>{e(r['nombre'])}</td><td>{e(r['direccion'])} {e(r['cp'])}</td><td>{lk(r['web'],'web')}</td><td>{e(r['telefono'])}</td><td>{e(r['espera_practicas'])}{' ('+lk(r['fuente_espera'],'fuente')+')' if r['fuente_espera'] else ''}</td><td>{e(r['aprobados_practico_B'])}{' · '+e(r['periodo_dgt'])+' · '+lk(r['fuente_dgt'],'DGT') if r['fuente_dgt'] else ''}</td><td>{lk(r['fuente'],'fuente')}</td></tr>" for r in rows)
page("index.html","Autoescuelas en Valencia ciudad",f'<p class="nota">Aún no tenemos datos verificados de tiempos de espera para prácticas o examen. No mostramos precios. Tasa DGT 2.1 de examen: 94,05 € (<a href="https://sede.dgt.gob.es/es/permisos-de-conducir/obtencion-y-gestion-de-permisos/solicitud-de-prueba-de-aptitud-de-examen/index.html">sede DGT</a>), da derecho a dos convocatorias.</p><p>{len(rows)} autoescuelas. Ver también los <a href="centros-examen.html">aprobados por centro de examen</a>. Aprobados: % de aptos en la prueba de circulación del permiso B, todas las secciones del código DGT, 10/2025–09/2026, microdatos oficiales DGT. Asociación nombre→código DGT hecha por nombre.</p><table><tr><th>Nombre</th><th>Dirección</th><th>Web</th><th>Teléfono</th><th>Espera prácticas/examen</th><th>Aprobados práctico B (DGT)</th><th>Fuente</th></tr>{tr}</table>')
page("como-elegir.html","Cómo elegir autoescuela si hay lista de espera","""<p>Mucha gente en Valencia se queja de esperas largas: <a href="https://www.reddit.com/r/valencia/comments/1syr0j0/es_normal_que_una_autoescuela_te_haga_esperar/">Reddit r/valencia</a>, <a href="https://www.reddit.com/r/askspain/comments/1p8c0f0/retraso_intencionado_de_autoescuela_sospecha_de/">7 meses esperando (r/askspain)</a>, <a href="https://www.lasexta.com/motor/noticias/carnet-conducir-sigue-atascado-faltan-solo-examinadores-sobran-solo-alumnos_202610066ac4da3fa4297764c3aac2ae.html">La Sexta</a>.</p>
<ol><li><b>Pregunta por escrito</b> cuánto tardan hoy en dar la primera práctica y cuántos alumnos presentan a examen por ciclo.</li>
<li><b>Entiende el reparto:</b> la DGT asigna los huecos de examen a cada autoescuela con el sistema CAPA, según sus alumnos pendientes y con un factor corrector por porcentaje de aprobados (<a href="https://revista.dgt.es/es/reportajes/2021/01ENERO/0114-CAPA-prueba.shtml">Revista DGT</a>, <a href="https://www.cnmc.es/sites/default/files/5791040.pdf">CNMC</a>). Un buen índice de aprobados ayuda a la autoescuela a recibir más plazas.</li>
<li><b>Mira los aprobados públicos</b> por autoescuela (datos DGT recopilados en <a href="https://seguridad-vial.es/autoescuelas/valencia/valencia">seguridad-vial.es</a>).</li>
<li><b>Desconfía de “packs”</b> que te obligan a pagar muchas clases por adelantado y pide el desglose.</li>
<li><b>La tasa DGT es fija:</b> 94,05 € (tasa 2.1), con dos convocatorias (<a href="https://sede.dgt.gob.es/es/permisos-de-conducir/obtencion-y-gestion-de-permisos/solicitud-de-prueba-de-aptitud-de-examen/index.html">sede DGT</a>).</li></ol>""")
page("adelantar-examen.html","¿Pueden adelantarte el examen pagando? Lo que dice la DGT","""<p>Las fechas de examen práctico no se venden. Las gestiona la DGT y las solicita la autoescuela: “si te presentas a través de una autoescuela, será la propia escuela la que se encargue de presentar tu solicitud” (<a href="https://www.dgt.es/nuestros-servicios/permisos-de-conducir/obtener-un-nuevo-permiso-de-conducir/requisitos-preparacion-y-presentacion-a-examen/index.html">DGT</a>).</p>
<p>Cada Jefatura reparte su capacidad en ciclos de 5 a 15 días hábiles entre las autoescuelas según sus alumnos pendientes y su tasa de aprobados (sistema CAPA, Anexo IX del Reglamento General de Conductores): <a href="https://revista.dgt.es/es/reportajes/2021/01ENERO/0114-CAPA-prueba.shtml">Revista DGT</a>, <a href="https://www.cnmc.es/sites/default/files/5791040.pdf">informe CNMC</a>.</p>
<p>Lo único que pagas a la DGT es la tasa 2.1 de 94,05 € (<a href="https://sede.dgt.gob.es/es/permisos-de-conducir/obtencion-y-gestion-de-permisos/solicitud-de-prueba-de-aptitud-de-examen/index.html">sede DGT</a>). Ningún pago oficial adelanta tu turno. Lo que una autoescuela decida sobre a qué alumnos presenta dentro de su cupo depende de ella: pide que te expliquen su criterio por escrito.</p>""")
import json
C=json.load(open(os.path.join(D,"data/centros_examen_valencia.json")))
M={}
for k,v in C.items():
    n="Valencia (ciudad)" if k.startswith("Valencia") else k
    for t,a in v.items():
        b=M.setdefault(n,{}).setdefault(t,[0,0,0]); b[0]+=a[0]; b[1]+=a[1]; b[2]+=a[2]
pc=lambda a:f"{100*a[0]/(a[0]+a[1]):.1f}% ({a[0]:,}/{a[0]+a[1]:,})".replace(",",".") if a and a[0]+a[1] else "sin datos"
FD="https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/conductores-autoescuelas.html"
trc="".join(f"<tr><td>{e(n)}</td><td>{pc(v.get('teorico'))}</td><td>{pc(v.get('practico'))}</td></tr>" for n,v in sorted(M.items(),key=lambda x:-sum(x[1].get('practico',[0,0])[:2])))
page("centros-examen.html","Centros de examen DGT en la provincia de Valencia: aprobados del permiso B",f"""<p>Porcentaje de aptos en el examen teórico y en el práctico (prueba de conducción y circulación) del permiso B en cada centro de examen de la provincia de Valencia, sumando octubre de 2025 a septiembre de 2026. Fuente: microdatos oficiales de la DGT por autoescuela (<a href="{FD}">DGT, listados de autoescuelas</a>). Entre paréntesis, aptos / exámenes realizados.</p>
<table><tr><th>Centro de examen</th><th>Teórico B</th><th>Práctico B</th></tr>{trc}</table>
<p class="nota">Lo que estos datos no dicen: tiempos de espera para examen (sin datos), direcciones y horarios de cada centro (sin datos verificados aquí; consulta la <a href="https://www.dgt.es/">web oficial de la DGT</a>). Un porcentaje alto o bajo no implica que un centro sea más fácil: depende también de los alumnos que se presentan. En los microdatos, la ciudad aparece como «Valencia/València (municipio sin especificar)»; se ha sumado una fila «Valencia» con 1 examen.</p>
<p>Normalmente no eliges centro: la solicitud la tramita tu autoescuela ante la DGT (<a href="https://www.dgt.es/nuestros-servicios/permisos-de-conducir/obtener-un-nuevo-permiso-de-conducir/requisitos-preparacion-y-presentacion-a-examen/index.html">DGT</a>). Ver también <a href="adelantar-examen.html">si se puede adelantar el examen pagando</a> y el <a href="index.html">listado de autoescuelas</a>.</p>""")
# verify
ok=True
for f in os.listdir(OUT):
    for h in re.findall(r'href="([^"]+)"',open(os.path.join(OUT,f)).read()):
        if not h.startswith("http") and not os.path.exists(os.path.join(OUT,h)): print("ROTO",f,h); ok=False
print("filas",len(rows),"paginas",sorted(os.listdir(OUT)),"enlaces_internos_ok",ok)
