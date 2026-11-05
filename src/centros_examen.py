# Aprobados permiso B por centro de examen, provincia de Valencia, microdatos DGT 10/2025-09/2026
import csv,glob,os,json
D=os.path.dirname(os.path.abspath(__file__))
agg={}
for f in sorted(glob.glob(os.path.join(D,"data/dgt/*.txt"))):
    for r in csv.DictReader(open(f,encoding="latin1"),delimiter=";"):
        if r["DESC_PROVINCIA"].startswith("Valencia") and r["NOMBRE_PERMISO"].strip()=="B":
            t="teorico" if r["TIPO_EXAMEN"].startswith("PRUEBA TE") else ("practico" if r["TIPO_EXAMEN"].startswith("PRUEBA CONDUCCI") else None)
            if not t: continue
            a=agg.setdefault(r["CENTRO_EXAMEN"].strip(),{}).setdefault(t,[0,0,0])
            a[0]+=int(r["NUM_APTOS"]); a[1]+=int(r["NUM_NO_APTOS"]); a[2]+=int(r["NUM_APTOS_1conv"])
json.dump(agg,open(os.path.join(D,"data/centros_examen_valencia.json"),"w"),ensure_ascii=False,indent=1)
print(json.dumps(agg,ensure_ascii=False))
