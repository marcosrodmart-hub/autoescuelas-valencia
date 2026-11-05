# Tasa de aprobados práctico B (PRUEBA CONDUCCIÓN Y CIRCULACIÓN, permiso B) desde microdatos DGT 10/2025-09/2026
import csv,glob,os
D=os.path.dirname(os.path.abspath(__file__))
MAP={"Autoescuelas El Cid AVAE":"V 0083","Autoescuelas Jordá Ramón Llull":"V 0982","Autoescuelas Jordá Blasco Ibáñez":"V 0982","Autoescuelas Colón":"V 0624","Autoescuelas Vallbona":"V 0808","Autoescuela Argente":"V 0477","Autoescuela Universitaria":"V 0869","Autoescuela 31 AVAE":"V 0983","Autoescuela Benicalap":"V 0746","Arcen Autoescuelas":"V 0680","Autoescuela Campanar":"V 0886","Autoescuela Tres Forques":"V 1020","Autoescuela San Cristóbal":"V 0012","Gran Vía 46 Auto Escuela":"V 0846","Autoescuela Maeztu":"V 0081","Autoescuela Area 91":"V 0774","Autoescuela Yeves":"V 0511","Autoescuela Clase":"V 0911"}
agg={}
for f in sorted(glob.glob(os.path.join(D,"data/dgt/*.txt"))):
    for r in csv.DictReader(open(f,encoding="latin1"),delimiter=";"):
        if r["DESC_PROVINCIA"].startswith("Valencia") and r["TIPO_EXAMEN"].startswith("PRUEBA CONDUCCI") and r["NOMBRE_PERMISO"].strip()=="B":
            a=agg.setdefault(r["CODIGO_AUTOESCUELA"],[0,0]); a[0]+=int(r["NUM_APTOS"]); a[1]+=int(r["NUM_NO_APTOS"])
p=os.path.join(D,"data/autoescuelas_valencia.csv"); rows=list(csv.DictReader(open(p)))
for r in rows:
    c=MAP.get(r["nombre"]); a=agg.get(c)
    if a and sum(a):
        r.update(codigo_dgt=c,aprobados_practico_B=f"{100*a[0]/sum(a):.1f}% ({a[0]}/{sum(a)})",periodo_dgt="10/2025–09/2026",fuente_dgt="https://www.dgt.es/menusecundario/dgt-en-cifras/matraba-listados/conductores-autoescuelas.html")
    else: r.update(codigo_dgt="",aprobados_practico_B="sin datos",periodo_dgt="",fuente_dgt="")
w=csv.DictWriter(open(p,"w",newline=""),fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
print(sum(r["aprobados_practico_B"]!="sin datos" for r in rows),"con dato de",len(rows))
