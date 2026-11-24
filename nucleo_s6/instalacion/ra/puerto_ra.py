"""Puerto aislado EQ/EQM/QSEN2; sin cambio de algoritmos ni parametros.
rem70 (P2-AREA-RA): vive en <instalación>/ra/ y resuelve TODO desde la instalación efectiva: C = la instalación (núcleo y herramientas/b),
RA = <instalación>/ra (historico/ y puerto/), manifiesto <instalación>/ra/R_A_dependencias.json; el área histórica, por la ruta ABSOLUTA
declarada en el manifiesto (anclada por su inventario en r1_rutas.ENTREGAS). Sin área de preparación. Se retiran los modos del ensayo i2
(admision_trabajador/ensayar/ejecutar), que dependían del área de ese ensayo; la producción solo usa ImportadorRA (evaluadores_ra.cargar).
Uso inocuo: python -B puerto_ra.py conexion <informe>
"""
from pathlib import Path
import hashlib,importlib,json,os,sys,types
A=Path(__file__).resolve().parents[1];P=A.parents[1];C=A;RA=A/'ra'
sys.path[:0]=[str(C/'src'),str(C/'herramientas/b'),str(P)]
import r1_rutas as RR
J=lambda p:json.loads(Path(p).read_bytes())
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
DEP=J(RA/'R_A_dependencias.json')
ENTRY={'EQ':'codigo.ensayo_quiebres','EQM':'codigo.ensayo_quiebres_macro','QSEN2':'codigo.sensibilidad_q'}

def configurar_importaciones(despliegue):
    """S6 exige verificadores de SU raíz, no mismos nombres del original.
    El núcleo candidato sigue primero. No se reemplazan módulos ya cargados.
    """
    root=Path(J(despliegue)['raiz_proyecto']).resolve()
    for n,m in list(sys.modules.items()):
        if n=='herramientas' or n.startswith('herramientas.'):
            p=getattr(m,'__file__',None)
            RR.need(not p or Path(p).resolve().is_relative_to(root),'R_A_MODULO_AUTORIDAD_AJENO',n)
    sys.path[:0]=[str(C/'src'),str(C/'herramientas/b'),str(root),str(root/'src')]
    return root

def construir_contexto(despliegue):
    configurar_importaciones(despliegue)
    import seleccion_paso4 as SP
    SP.configurar(despliegue)
    return SP.contexto()

class ImportadorRA(RR.ImportadorEntrega):
    def __init__(self,ctx,salida):
        super().__init__(Path(DEP['historico']).parent,Path(DEP['historico']).name,C/'src/paper2b',ctx)
        self.salida=Path(salida).resolve()
    def _portar(self,f):
        rel=Path(f).relative_to(self.area).as_posix()
        rec=next((x for x in DEP['codigo'].values() if x['archivo']==rel),None)
        RR.need(rec is not None,'MODULO_FUERA_DEL_CIERRE_TRANSITIVO',rel)
        hist,port=RA/'historico'/rel,RA/'puerto'/rel
        RR.need(H(hist)==rec['sha256']==H(f) and H(port)==rec['puerto']['sha256'],'PUERTO_O_FUENTE_ALTERADO',rel)
        return rel,hist.read_bytes(),port.read_text(encoding='utf-8'),rec['sustituciones']
    def exec_module(self,m):
        super().exec_module(m)
        if m.__name__=='codigo.demo.nucleo_v':
            # AREA/ROOT de lectura historica se conservan (RES usa AREA.parent).
            # Solo se redirige la escritura a la salida AISLADA de este intento.
            def escribir(path,obj):
                path=Path(path).resolve();RR.need(path.is_relative_to(self.salida),'ESCRITURA_FUERA_DE_R_A')
                path.parent.mkdir(parents=True,exist_ok=True)
                raw=(json.dumps(obj,indent=1,ensure_ascii=False,sort_keys=True,default=str)+'\n').encode()
                tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_bytes(raw);os.replace(tmp,path)
                return hashlib.sha256(raw).hexdigest()
            m.write_json_atomic=escribir

def conexion(out):
    ctx=types.SimpleNamespace(PRUEBA='SOLO IDENTIDAD DE OBJETO; SIN CONSTRUIR CONTEXTO')
    imp=ImportadorRA(ctx,Path(out).parent);imp.instalar()
    for m in ENTRY.values():importlib.import_module(m)
    N=importlib.import_module('codigo.demo.nucleo_v');assert N.Contexto() is ctx
    assert 'codigo.demo.c2_normalizado' in imp.registro
    imp.guarda()
    modulos={n:{'archivo':str(Path(m.__file__).resolve()),'sha256':H(m.__file__)} for n,m in list(sys.modules.items()) if getattr(m,'__file__',None) and Path(m.__file__).is_file() and (n.startswith(('codigo.','paper2b.','paper2.','herramientas.')))}
    runtime={n:{'archivo':str(Path(m.__file__).resolve()),'sha256':H(m.__file__)} for n,m in list(sys.modules.items()) if getattr(m,'__file__',None) and Path(m.__file__).is_file()}
    Path(out).write_text(json.dumps(dict(runtime_cargado=runtime,conforme=True,ciencia_ejecutada=False,contexto_s6_construido=False,modulos_historicos=imp.registro,importaciones_efectivas=modulos,
        limitacion='Conexion de importaciones y sustitucion de Contexto; no equivalencia cientifica.'),indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps(dict(conforme=True,modulos_historicos=len(imp.registro),importaciones_efectivas=len(modulos))))

if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='conexion':conexion(sys.argv[2])
    else:raise SystemExit('Use conexion <informe> (producción: evaluadores_ra.cargar)')
