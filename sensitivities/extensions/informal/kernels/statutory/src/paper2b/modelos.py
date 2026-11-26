"""Proveedores de modelo para Paquete B.

- `ModeloTeorico` (el modelo v2.2 del proyecto) con ENCIERROS DEMOSTRATIVOS (encierros_modelo.py; fundamento en
  review/FUNDAMENTO_ENCIERROS.md): C2 por rama y cota con cotas inferior y superior demostradas; evidencia 2-D de
  CS - K1 para R1, evidencia 1-D por sección para R2, perfil C2(phi) con derivada de Danskin encerrada y encierro de C2
  sobre cajas de primitivas estructurales. Lo que el encierro no resuelve (presupuesto, cajas que tocan una curva de
  salto con rho = 1, raíces múltiples) queda `incomplete` con motivo; nunca se completa con mallas ni residuos.
- `ModeloTeoricoSinEncierros`: el MISMO modelo sin encierros (C2 por mallas con error ESTIMADO; R1/R2/endógenas/
  cobertura sin certificar). Rotulado con otro `kind`; sirve para pruebas de plomería rápidas y como contraste.
- `SustitutoCertificado` (FICTICIO, solo validación): modelo analítico separable con extensiones por intervalos exactas
  que permite probar de punta a punta la ruta certificada (supremo por rama y cota, R1/R2/raíces endógenas completas,
  cobertura estructural por cajas). Está rotulado y la ruta oficial lo rechaza.
CS(tau; theta) = d_v * (alpha(theta) tau_d (1 - tau_d) + beta(theta) tau_f (1 - tau_f)), B_pot = 1, con
alpha = 0.6 + 0.2 phi + 0.1 (a - 1) - 0.05 kappa_tilde y beta = 0.4 + 0.3 phi - 0.1 rho + 0.05 eta_f (afines).
"""
from __future__ import annotations

import math
from collections import OrderedDict
from dataclasses import dataclass

from . import elementales as EL
from . import encierros_modelo as EM
from . import frontier as FR
from . import model as M
from .intervalos import Iv
from .supremum import SupConfig, SupResult, axes, certified_supremum, nodes

SURROGATE_TAG = "SUSTITUTO_ANALITICO_CERTIFICADO_FICTICIO"
WIDE = Iv(-math.inf, math.inf)


def _up(x: float) -> float:
    return math.nextafter(x, math.inf)


class ModeloTeoricoSinEncierros:
    """Modelo v2.2 sin encierros: C2 con error ESTIMADO y ninguna evidencia demostrativa (todo lo que exige
    cobertura certificada queda `incomplete`)."""
    kind = "modelo_teorico_v2_2_sin_encierros"
    certified = False
    fictitious = False

    def derive(self, values):
        return M.derive(values)

    def state(self, values):
        return M.state_from_primitives(values)

    def evaluate(self, state, td, tf, design):
        return M.evaluate(state, td, tf, design)

    def capture_ceiling(self, state, design, j, bd, bf, available, cfg):
        return FR.capture_ceiling(state, design, j, bd, bf, available, cfg)

    def frontier_grid(self, state, design, j, bd, bf, n):
        return FR.frontier_grid(state, design, j, bd, bf, n)

    def contour_evidence(self, state, design, K1):
        return None

    def path_evidence(self, state, design, section, rate, K1):
        return None

    def c2_param_evidence(self, values, design, j, param, bd, bf):
        return None

    def c2_struct_enclosure(self, box: dict, design, j, bd, bf, fixed=None):
        return None


class ModeloTeorico(ModeloTeoricoSinEncierros):
    """Modelo v2.2 con encierros demostrativos (ver encabezado). La certificación exige la plataforma IEEE 754 binary64 con
    redondeo al más cercano comprobada por paper2b.elementales: sin ella el proveedor NO es certificado y se comporta como
    ModeloTeoricoSinEncierros (C2 como estimación, sin evidencia demostrativa), nunca como certificado condicionado."""
    kind = "modelo_teorico_v2_2_incidencia_estatutaria"

    @property
    def certified(self) -> bool:
        return EL.GARANTIA is not None

    @property
    def garantia(self) -> str | None:
        """Base de las cotas: 'ieee754_binary64_rn' o None (plataforma no conforme)."""
        return EL.GARANTIA

    def __init__(self, *, sup_max_boxes: int = 20000, jump_budget: int = 600, point_tol: float = 2e-14,
                 param_d1_tol: float = 1e-6, param_max_boxes: int = 3000, param_d1_boxes: int = 400,
                 param_d1_refine: int = 1500, param_goal_boxes: int = 400, param_budget_s: float = 3600.0,
                 struct_tol: float = 1e-4,
                 struct_max_boxes: int = 400, engines: int = 64):
        self.sup_max_boxes, self.jump_budget = sup_max_boxes, jump_budget
        self.point_tol, self.param_d1_tol, self.param_max_boxes = point_tol, param_d1_tol, param_max_boxes
        self.param_d1_boxes, self.param_budget_s = param_d1_boxes, param_budget_s
        self.param_d1_refine, self.param_goal_boxes = param_d1_refine, param_goal_boxes
        self.struct_tol, self.struct_max_boxes = struct_tol, struct_max_boxes
        self._engines: OrderedDict = OrderedDict()
        self._n_engines = engines

    def engine(self, state, design) -> EM.Engine:
        key = (state, design)
        eng = self._engines.get(key)
        if eng is None:
            eng = self._engines[key] = EM.Engine(EM.IParams.from_state(state), design)
            if len(self._engines) > self._n_engines:
                self._engines.popitem(last=False)
        else:
            self._engines.move_to_end(key)
        return eng

    # ------------------------------------------------------------------------------------ techo de captura
    def capture_ceiling(self, state, design, j, bd, bf, available, cfg: SupConfig):
        """C2 por rama y cota: C2 informado = mejor valor evaluado / B_pot y numerical_error = COTA demostrada de
        |C2 - sup| (el supremo está entre las cotas inferior y superior demostradas). Alcanzado si ninguna caja viva toca
        una curva de salto (R continua en la unión compacta de cajas vivas); si alguna la toca tras el presupuesto de
        refinamiento, `incomplete` (no se afirma alcance ni no alcance)."""
        if not available:
            return FR.Ceiling(False, None, None, state.B_pot, None, "not_applicable", "INSTRUMENT_NOT_AVAILABLE")
        if not self.certified:
            return super().capture_ceiling(state, design, j, bd, bf, available, cfg)
        eng = self.engine(state, design)
        Bi = eng.P.B_pot
        B = state.B_pot
        sb = EM.sup_bound(eng, j, bd, bf, tol=0.5 * cfg.tol_converge * Bi.lo, max_boxes=self.sup_max_boxes,
                          value=lambda x, y: M.revenue(state, x, y, design), jump_budget=self.jump_budget)
        lo_s = (Iv.point(sb.lower) / Bi).lo
        hi_s = (Iv.point(sb.upper) / Bi).hi
        C2 = sb.approx / B
        err = _up(max(0.0, hi_s - C2, C2 - lo_s))
        res = SupResult(sup=sb.approx, attained=not sb.jump_live, tau_d=sb.point[0], tau_f=sb.point[1],
                        lateral_low=None, lateral_high=None)
        res.error_kind, res.upper, res.lower = "certified_bound", sb.upper, sb.lower
        res.numerical_error = err * B
        res.level_values = [sb.approx]
        res.final_n = sb.boxes
        if sb.jump_live:
            res.converged, res.status, res.reason = False, "incomplete", "SUP_ATTAINMENT_UNDECIDED_AT_JUMP_CURVE"
        elif err > cfg.tol_converge:
            res.converged, res.status, res.reason = False, "incomplete", "CERTIFIED_BOUND_NOT_CLOSED"
        else:
            res.converged, res.status, res.reason = True, "complete", None
        return FR.Ceiling(True, res, C2, B, err, res.status, res.reason)

    # ------------------------------------------------------------------------------------ evidencia R1 (2-D)
    def contour_evidence(self, state, design, K1):
        from .contour import Evidence2D
        if not self.certified:
            return None
        eng = self.engine(state, design)
        Bi = eng.P.B_pot

        def rng(x0, x1, y0, y1):
            e, _ = eng.R_box_g(Iv(x0, x1), Iv(y0, y1))
            return e / Bi - K1

        def grad(x0, x1, y0, y1, k):
            _, g, _ = eng.R_full(Iv(x0, x1), Iv(y0, y1), grad=True)
            return WIDE if g is None else g[k] / Bi

        def pt(x, y, k):
            gk = grad(x, x, y, y, k)
            return 0.5 * (gk.lo + gk.hi) if math.isfinite(gk.lo) and math.isfinite(gk.hi) else 0.0
        ev = Evidence2D(range=rng, dx=lambda *b: grad(*b, 0), dy=lambda *b: grad(*b, 1), dxx=lambda *b: WIDE,
                        dyy=lambda *b: WIDE, fx=lambda x, y: pt(x, y, 0), fy=lambda x, y: pt(x, y, 1),
                        source=self.kind + ":encierros_modelo")
        # INTEGRACIÓN 3.7: pliegue y gradientes de rama del motor para la dirección adaptativa de R1
        ev.ramas = lambda x0, x1, y0, y1: eng.R_full(Iv(x0, x1), Iv(y0, y1), grad=True)
        return ev

    # ------------------------------------------------------------------------------------ evidencia R2 (1-D)
    def path_evidence(self, state, design, section, rate, K1):
        from .raices import Evidence1D
        if not self.certified:
            return None
        eng = self.engine(state, design)
        Bi = eng.P.B_pot
        Z = Iv(0.0, 0.0)
        if section == "tau_f_0":
            box, comb = (lambda a, b: (Iv(a, b), Z)), (lambda g: g[0])
        elif section == "tau_d_0":
            box, comb = (lambda a, b: (Z, Iv(a, b))), (lambda g: g[1])
        elif section == "paridad":
            box, comb = (lambda a, b: (Iv(a, b), Iv(a, b))), (lambda g: g[0] + g[1])
        elif section == "tau_d_estatutario":
            if rate is None:
                return None
            box, comb = (lambda a, b: (Iv(rate, rate), Iv(a, b))), (lambda g: g[1])
        else:
            return None

        def rng(a, b):
            e, _ = eng.R_box_g(*box(a, b))
            return e / Bi - K1

        def d1(a, b):
            _, g, _ = eng.R_full(*box(a, b), grad=True)
            return WIDE if g is None else comb(g) / Bi

        def deriv(x):
            d = d1(x, x)
            return 0.5 * (d.lo + d.hi) if math.isfinite(d.lo) and math.isfinite(d.hi) else 0.0
        return Evidence1D(range=rng, d1=d1, d2=None, deriv=deriv, source=self.kind + ":encierros_modelo")

    # ------------------------------------------------------------------------------------ perfil C2(phi)
    def c2_param_evidence(self, values, design, j, param, bd, bf, limite=None):
        """Evidencia de C2(phi) en [0, 1]. `limite` (INTEGRACIÓN 3.7, paso 12): plazo absoluto en time.monotonic() común a
        la inversión; agotado -> EvidenceBudgetExhausted en el siguiente encierro (búsqueda incompleta, nunca inexistencia).

        range(a, b): encierro de {C2(phi): phi en [a, b]} = [max_tau R(tau, Phi).lo, cota superior de rama y cota con
        Phi] / B_pot; range_goal: lo mismo, detenido en cuanto decide el signo frente a un nivel. Si el maximizador
        estimado está en un quiebre "min", la rama y cota se hace en coordenadas CORTADAS tau' = tau - sigma (phi - m) e_i
        (FUNDAMENTO_COTAS §3, EM.sup_bound_shear): el encierro sigue siendo válido para cualquier sigma, y con sigma que
        iguala las tasas de las ramas su ancho sigue la variación real de C2 y no la de R a tau fijo.
        d1(a, b): encierro de TODA pendiente secante de C2 en [a, b] (FUNDAMENTO_COTAS §4, Lema de perturbación):
          - caja viva con R suave: envolvente de dR/dphi (Danskin por secantes);
          - caja viva con quiebre "min" (R = min(f1, f2), Lema 3): tau se desplaza sigma (phi' - phi) a lo largo de un eje
            libre; entonces C2(phi') >= C2(phi) + (phi' - phi) min_k rate_k, rate_k = df_k/dphi + sigma df_k/dtau_i, con
            gradientes de rama encerrados sobre la caja expandida x Phi. Vale para CUALQUIER sigma; se elige sigma que
            iguala las tasas de las dos ramas (la envolvente de Clarke, en cambio, contiene ambos signos).
        Las cajas vivas cubren los maximizadores de todo phi en [a, b] (solo se poda con cota superior < inferior).
        Presupuesto: param_budget_s segundos por evidencia; agotado, raices.EvidenceBudgetExhausted -> búsqueda incompleta.
        Una rama y cota dirigida a un nivel (range_goal) sobre un intervalo se detiene a las param_goal_boxes cajas: si
        el nivel está dentro del rango real de C2 en el intervalo no se puede decidir, y subdividir es más barato que
        seguir afinando (solo decide cuándo parar; el encierro devuelto es válido)."""
        if param != "phi" or j not in ("f", "df") or not self.certified:
            return None
        import time as _time
        from .raices import Evidence1D, EvidenceBudgetExhausted
        state = M.state_from_primitives(dict(values, phi=0.5))
        eng = self.engine(state, design)
        Bi = eng.P.B_pot
        cache: dict = {}
        t_start = [None]
        stats = {"sup_bound": 0, "sup_corte": 0, "segundos": 0.0, "d1_perturbacion": 0, "d1_envolvente": 0,
                 "d1_sin_cota": 0, "s_punto": 0.0, "s_corte": 0.0, "s_plano": 0.0, "s_d1_refino": 0.0, "registro": []}
        (dl, dh), (fl, fh) = axes(j, bd, bf)
        bounds_ax = ((dl, dh), (fl, fh))
        free = [k for k, (lo_, hi_) in enumerate(bounds_ax) if hi_ > lo_]
        hints: dict = {}        # (a, b) -> (m, maximizador aproximado en coordenadas reales en phi = m, sigma, eje)

        def mid(v):
            return 0.5 * (v.lo + v.hi)

        def shear_for(a, b):
            """(sigma, eje, m, semilla) para [a, b], o None (rama y cota a tau fijo). sigma iguala las tasas en phi de las
            dos ramas del quiebre "min" en el maximizador estimado (Danskin con multiplicador); el maximizador se estima
            desde el intervalo ya evaluado más estrecho que contiene a [a, b]. Solo decide la estrechez, no el rigor."""
            if not free:
                return None
            ref = None
            for (a0, b0), h in hints.items():
                if a0 <= a and b <= b0 and (ref is None or b0 - a0 < ref[0]):
                    ref = (b0 - a0, h)
            if ref is None:
                return None
            mp, (px, py), sp, ap = ref[1]
            m = 0.5 * (a + b)
            if ap is not None:
                px, py = (px + sp * (m - mp), py) if ap == 0 else (px, py + sp * (m - mp))
            px, py = min(max(px, dl), dh), min(max(py, fl), fh)
            for r in (1e-7, 1e-5, 1e-3):
                X = Iv(max(dl, px - r), min(dh, px + r))
                Y = Iv(max(fl, py - r), min(fh, py + r))
                _, g, br = eng.R_full(X, Y, Iv(m, m), grad=True)
                if g is None or (br is not None and br["kind"] == "jump"):
                    return None
                if br is None:
                    continue
                if br["kind"] != "min":
                    return None
                go, gi = br["g_out"], br["g_in"]
                i = max(free, key=lambda k: abs(mid(go[k]) - mid(gi[k])))
                den = mid(go[i]) - mid(gi[i])
                sigma = (mid(gi[2]) - mid(go[2])) / den if den != 0.0 else 0.0
                if sigma == 0.0 or not math.isfinite(sigma):
                    return None
                return sigma, i, m, (px, py)
            return None

        def decides(level, lower, upper):
            """El encierro de C2 que recibirá el llamador (la misma cuenta que enc: [inferior, superior] / B_pot con
            B_pot por intervalos) excluye el nivel. Decidir en unidades de R con B_pot central no basta: en el borde
            (|C2 - nivel| del orden del ancho relativo de B_pot) la rama y cota pararía sin que el llamador pueda
            decidir, con un encierro ancho del otro lado."""
            e = Iv(lower, max(lower, upper)) / Bi
            return e.hi < level or e.lo > level

        def run(a, b, *, goal=None, purpose="range"):
            """Encierro del supremo sobre phi en [a, b]. purpose "range": tolerancia de rango (piso alcanzable) y
            param_max_boxes; "d1": param_d1_tol y param_d1_boxes (solo se usan sus cajas vivas y su cota inferior).
            `goal`: nivel de C2; la rama y cota se detiene cuando decides() lo excluye. Un resultado ya calculado del
            mismo intervalo que ya decide el nivel se reutiliza."""
            for k in ((a, b, purpose, goal), (a, b, purpose, None)):
                if k in cache:
                    return cache[k]
            if goal is not None:
                for (a0, b0, _, _), sb0 in cache.items():
                    if a0 == a and b0 == b and decides(goal, sb0.lower, sb0.upper):
                        return sb0
            now = _time.time()
            if t_start[0] is None:
                t_start[0] = now
            if limite is not None and _time.monotonic() > limite:
                raise EvidenceBudgetExhausted("c2_param_evidence: plazo común de la inversión agotado")
            if now - t_start[0] > self.param_budget_s:
                raise EvidenceBudgetExhausted("c2_param_evidence: %.0f s" % (now - t_start[0]))
            if purpose == "d1":
                boxes = self.param_d1_boxes
            elif goal is not None and a < b:
                boxes = self.param_goal_boxes
            else:
                boxes = self.param_max_boxes
            t_run = _time.time()
            stop = None if goal is None else (lambda lo_, hi_: decides(goal, lo_, hi_))
            sh = shear_for(a, b) if a < b else None
            start = warm_start(a) if a == b else None
            if sh is not None:
                sigma, i, m, seed = sh
                tol = (self.point_tol if purpose == "range" else self.param_d1_tol) * Bi.lo
                sb = EM.sup_bound_shear(eng, j, bd, bf, tol=tol, Phi=Iv(a, b), sigma=sigma, axis=i, m=m,
                                        max_boxes=boxes, goal=stop, seed=seed)
                stats["sup_corte"] += 1
                if sb.point[0] is not None:
                    hints[(a, b)] = (m, sb.point, sigma, i)
            else:
                tol = floor(a, b) if purpose == "range" else max(self.param_d1_tol * Bi.lo, floor(a, b))
                sb = EM.sup_bound(eng, j, bd, bf, tol=tol, max_boxes=boxes, Phi=Iv(a, b), jump_budget=0, goal=stop,
                                  start=start)
                if a < b and sb.point[0] is not None:
                    hints.setdefault((a, b), (0.5 * (a + b), sb.point, 0.0, None))
            stats["sup_bound"] += 1
            dt = _time.time() - t_run
            kind_run = "punto" if a == b else ("corte" if sh is not None else "plano")
            stats["s_" + kind_run] = round(stats["s_" + kind_run] + dt, 1)
            stats["registro"].append((a, b, purpose, goal is not None, kind_run, sb.boxes, round(dt, 1),
                                      sb.lower / Bi.lo, sb.upper / Bi.lo))
            stats["segundos"] = round(_time.time() - t_start[0], 1)
            cache[(a, b, purpose, goal)] = sb
            return sb

        def warm_start(x):
            """Cajas iniciales para evaluar en el punto x: las cajas vivas de la rama y cota ya hecha sobre el intervalo
            más estrecho [a0, b0] que contiene x (fuera de ellas R(., x) < cota inferior demostrada <= C2(x) B_pot:
            sup_bound(start=...) es válido). Si esa rama y cota fue cortada, las cajas se trasladan por el encierro de
            sigma (x - m) a lo largo del eje de corte y se recortan al menú. None: menú completo."""
            ref = None
            for (a0, b0, _, _), sb0 in cache.items():
                if a0 < b0 and a0 <= x <= b0 and sb0.live:
                    key = (b0 - a0, len(sb0.live))
                    if ref is None or key < ref[0]:
                        ref = (key, sb0)
            if ref is None:
                return None
            sb0 = ref[1]
            if sb0.shear is None:
                return list(sb0.live)
            sigma, i, m, _ = sb0.shear
            s = Iv.point(sigma) * (Iv.point(x) - m)
            out = []
            for (x0, x1, y0, y1) in sb0.live:
                if i == 0:
                    x0, x1 = max(dl, EL.dn(x0 + s.lo)), min(dh, EL.up(x1 + s.hi))
                else:
                    y0, y1 = max(fl, EL.dn(y0 + s.lo)), min(fh, EL.up(y1 + s.hi))
                if x0 <= x1 and y0 <= y1:
                    out.append((x0, x1, y0, y1))
            return out or None

        def live_real(sb):
            """Cajas vivas en coordenadas reales: las de una rama y cota cortada se amplían en E a lo largo del eje de
            corte (tau = tau' + sigma (phi - m) e_i, |sigma (phi - m)| <= E) y se recortan al menú."""
            if sb.shear is None:
                return list(sb.live)
            _, i, _, E = sb.shear
            out = []
            for (x0, x1, y0, y1) in sb.live:
                if i == 0:
                    x0, x1 = max(dl, EL.dn(x0 - E)), min(dh, EL.up(x1 + E))
                else:
                    y0, y1 = max(fl, EL.dn(y0 - E)), min(fh, EL.up(y1 + E))
                if x0 <= x1 and y0 <= y1:
                    out.append((x0, x1, y0, y1))
            return out
        floors: dict = {}

        def floor(a, b):
            """Tolerancia alcanzable: con phi en un intervalo, la brecha [max_tau R(tau, Phi).lo, cota superior] no baja de
            la variación de R con phi en un punto (ancho de R(tau, Phi)); cerrar por debajo de eso solo gasta presupuesto.
            Esto no afecta el rigor (el encierro sigue siendo válido): solo cuándo se detiene la rama y cota."""
            if a == b:
                return self.point_tol * Bi.lo
            if (a, b) not in floors:
                c0, _ = eng.R(Iv.point(0.5 * (dl + dh)), Iv.point(0.5 * (fl + fh)), Iv(a, b))
                floors[(a, b)] = max(self.point_tol * Bi.lo, 2.0 * (c0.hi - c0.lo))
            return floors[(a, b)]

        def enc(sb):
            return Iv(sb.lower, max(sb.lower, sb.upper)) / Bi

        def rng_goal(a, b, level):
            return enc(run(a, b, goal=level))

        def rng(a, b):
            return enc(run(a, b))

        def secant_box(box, a, b):
            """Encierro (lo, hi) de las pendientes secantes aportadas por los maximizadores de esta caja, o None."""
            x0, x1, y0, y1 = box
            Phi = Iv(a, b)
            _, g, br = eng.R_full(Iv(x0, x1), Iv(y0, y1), Phi, grad=True)
            if g is None:
                stats["d1_sin_cota"] += 1
                return None
            clarke = (g[2].lo, g[2].hi)
            if not math.isfinite(clarke[0]) or not math.isfinite(clarke[1]):
                stats["d1_sin_cota"] += 1
                return None
            if br is None or br["kind"] != "min" or not free:
                stats["d1_envolvente"] += 1
                return clarke
            go, gi = br["g_out"], br["g_in"]
            i = max(free, key=lambda k: abs(mid(go[k]) - mid(gi[k])))
            den = mid(go[i]) - mid(gi[i])
            if den == 0.0 or not math.isfinite(den):
                stats["d1_envolvente"] += 1
                return clarke
            sigma = (mid(gi[2]) - mid(go[2])) / den
            ext = EL.up(abs(sigma) * (b - a))
            lo_i, hi_i = (x0, x1) if i == 0 else (y0, y1)
            elo, ehi = EL.dn(lo_i - ext), EL.up(hi_i + ext)
            if elo < bounds_ax[i][0] or ehi > bounds_ax[i][1]:
                stats["d1_envolvente"] += 1               # el desplazamiento saldría del menú: sin perturbación
                return clarke
            ex = (Iv(elo, ehi), Iv(y0, y1)) if i == 0 else (Iv(x0, x1), Iv(elo, ehi))
            _, g2, br2 = eng.R_full(ex[0], ex[1], Phi, grad=True)
            if g2 is None or br2 is None or br2["kind"] != "min":
                stats["d1_envolvente"] += 1
                return clarke
            rates = [G[2] + Iv.point(sigma) * G[i] for G in (br2["g_out"], br2["g_in"])]
            stats["d1_perturbacion"] += 1
            return min(r.lo for r in rates), max(r.hi for r in rates)

        def d1(a, b):
            """Envolvente de las cotas de pendiente de todas las (sub)cajas que pueden contener maximizadores. Una caja
            cuya cota contiene 0 se subdivide (la cota vale para cualquier subcaja: el maximizador está en alguna de
            ellas); una subcaja con R(caja, Phi).hi < cota inferior demostrada de min_phi C2 no contiene maximizadores y
            se descarta. Presupuesto: param_d1_refine evaluaciones por llamada (agotado: la envolvente alcanzada)."""
            # cualquier rama y cota ya hecha sobre [a, b] sirve (sus cajas vivas cubren los maximizadores de todo phi
            # de [a, b] y su cota inferior está demostrada); si no hay, una con la tolerancia de d1
            prev = [s for (a0, b0, _, _), s in cache.items() if a0 == a and b0 == b]
            sb = max(prev, key=lambda s: s.lower) if prev else run(a, b, purpose="d1")
            t_d1 = _time.time()
            Phi = Iv(a, b)
            stack = live_real(sb)
            lo = hi = None
            evals = 0
            # en intervalos anchos de phi la variación de los maximizadores impide excluir el 0 aunque se refine: el
            # presupuesto se concentra en intervalos finos (la búsqueda de raíces los produce al subdividir)
            budget = self.param_d1_refine if (b - a) <= 1e-3 else self.param_d1_refine // 10
            while stack:
                box = stack.pop()
                x0, x1, y0, y1 = box
                if evals >= budget:
                    r = secant_box(box, a, b)
                else:
                    evals += 1
                    e, _ = eng.R_box_g(Iv(x0, x1), Iv(y0, y1), Phi)
                    if e.hi < sb.lower:
                        continue                              # sin maximizadores para ningún phi de [a, b]
                    r = secant_box(box, a, b)
                    if r is not None and r[0] <= 0.0 <= r[1] and evals < budget:
                        # subdividir a lo largo del eje libre de mayor extensión relativa a la escala del gradiente
                        wx, wy = x1 - x0, y1 - y0
                        if wx > 0.0 and (wy == 0.0 or wx >= wy / 50.0):
                            m = 0.5 * (x0 + x1)
                            kids = ((x0, m, y0, y1), (m, x1, y0, y1))
                        elif wy > 0.0:
                            m = 0.5 * (y0 + y1)
                            kids = ((x0, x1, y0, m), (x0, x1, m, y1))
                        else:
                            kids = ()
                        if kids and kids[0] != box and kids[1] != box:
                            stack.extend(kids)
                            continue
                if r is None:
                    return WIDE
                lo = r[0] if lo is None else min(lo, r[0])
                hi = r[1] if hi is None else max(hi, r[1])
            stats["d1_evaluaciones"] = stats.get("d1_evaluaciones", 0) + evals
            stats["s_d1_refino"] = round(stats["s_d1_refino"] + _time.time() - t_d1, 1)
            return WIDE if lo is None else Iv(lo, hi) / Bi

        def deriv(x):
            d = d1(x, x)
            return 0.5 * (d.lo + d.hi) if math.isfinite(d.lo) and math.isfinite(d.hi) else 0.0
        ev = Evidence1D(range=rng, d1=d1, d2=None, deriv=deriv, source=self.kind + ":encierros_modelo:phi",
                        range_goal=rng_goal)
        ev.stats = stats
        return ev

    # ------------------------------------------------------------------------------------ cobertura estructural
    def c2_struct_enclosure(self, box: dict, design, j, bd, bf, fixed=None):
        """Encierro de C2 sobre una caja de primitivas estructurales (parámetros por intervalos; `fixed` aporta gamma y
        z_m). La admisibilidad de la caja la demuestra cobertura.box_admissible antes de llamar."""
        if fixed is None or not self.certified:
            return None
        P = EM.IParams.from_primitive_box(box, fixed)
        eng = EM.Engine(P, design)
        # con parámetros por intervalos el encierro puntual ya tiene ancho w0 > 0: cerrar la brecha por debajo de w0 es
        # imposible, así que la tolerancia de la rama y cota es max(struct_tol, w0) (la cobertura refina la caja)
        (dl, dh), (fl, fh) = axes(j, bd, bf)
        c0, _ = eng.R(Iv.point(0.5 * (dl + dh)), Iv.point(0.5 * (fl + fh)))
        tol = max(self.struct_tol * P.B_pot.lo, c0.hi - c0.lo)
        sb = EM.sup_bound(eng, j, bd, bf, tol=tol, max_boxes=self.struct_max_boxes, jump_budget=0)
        return Iv(sb.lower, max(sb.lower, sb.upper)) / P.B_pot


@dataclass
class _SState:
    alpha: float
    beta: float
    phi: float
    B_pot: float = 1.0


@dataclass
class _SEval:
    tau_d: float
    tau_f: float
    R: float
    B_d: float
    B_f: float
    B_pot: float
    topology: str = "SUR"


def _tt(a: float, b: float) -> Iv:
    """Rango EXACTO de t(1 - t) en [a, b] (cóncava, máximo en 1/2), ensanchado un ulp."""
    vals = [a * (1 - a), b * (1 - b)] + ([0.25] if a <= 0.5 <= b else [])
    return Iv(min(vals), max(vals)) + Iv(-1e-17, 1e-17)


def _m(bar: float) -> float:
    return bar * (1 - bar) if bar <= 0.5 else 0.25


class SustitutoCertificado:
    kind = SURROGATE_TAG
    certified = True
    fictitious = True
    DESIGN = {"G": 1.0, "N": 0.95}

    def derive(self, values):
        return M.derive(values)

    @staticmethod
    def alpha(v):
        return 0.6 + 0.2 * float(v["phi"]) + 0.1 * (float(v["a"]) - 1) - 0.05 * float(v["kappa_tilde"])

    @staticmethod
    def beta(v):
        return 0.4 + 0.3 * float(v["phi"]) - 0.1 * float(v["rho"]) + 0.05 * float(v["eta_f"])

    @staticmethod
    def alpha_iv(b):
        return 0.6 + 0.2 * Iv(*b["phi"]) + 0.1 * (Iv(*b["a"]) - 1) - 0.05 * Iv(*b["kappa_tilde"])

    @staticmethod
    def beta_iv(b):
        return 0.4 + 0.3 * Iv(*b["phi"]) - 0.1 * Iv(*b["rho"]) + 0.05 * Iv(*b["eta_f"])

    def state(self, values):
        return _SState(self.alpha(values), self.beta(values), float(values["phi"]))

    def cs(self, s, td, tf, design):
        d = self.DESIGN[design]
        return d * (s.alpha * td * (1 - td) + s.beta * tf * (1 - tf))

    def evaluate(self, s, td, tf, design):
        d = self.DESIGN[design]
        B_d, B_f = d * s.alpha * (1 - td), d * s.beta * (1 - tf)
        return _SEval(td, tf, td * B_d + tf * B_f, B_d, B_f, 1.0)

    def enclosure(self, s, design):
        d = self.DESIGN[design]
        return lambda x0, x1, y0, y1: d * (s.alpha * _tt(x0, x1) + s.beta * _tt(y0, y1))

    def capture_ceiling(self, s, design, j, bd, bf, available, cfg: SupConfig):
        if not available:
            return FR.Ceiling(False, None, None, 1.0, None, "not_applicable", "INSTRUMENT_NOT_AVAILABLE")
        res = certified_supremum(lambda x, y: self.cs(s, x, y, design), j, bd, bf, self.enclosure(s, design),
                                 tol=cfg.tol_attain)
        return FR.Ceiling(True, res, res.sup, 1.0, res.numerical_error, res.status, res.reason)

    def frontier_grid(self, s, design, j, bd, bf, n):
        (dl, dh), (fl, fh) = axes(j, bd, bf)
        dn = nodes(dl, dh, n) if dh > dl else [dl]
        fn = nodes(fl, fh, n) if fh > fl else [fl]
        rows = []
        for i, td in enumerate(dn):
            for k, tf in enumerate(fn):
                ev = self.evaluate(s, td, tf, design)
                eps = {"eps_dd": 1.0 if ev.B_d > 0 else None, "eps_df": 0.0 if ev.B_d > 0 else None,
                       "eps_fd": 0.0 if ev.B_f > 0 else None, "eps_ff": 1.0 if ev.B_f > 0 else None}
                sP = None if tf == 0.0 else M.provider_share(tf, s.phi)
                reason = "SP_LIMIT_AT_ZERO_RATE" if tf == 0.0 else None
                rows.append(FR.PointRow(f"P{i:04d}_{k:04d}", "point", td, tf, ev.B_d, ev.B_f, ev.R, 1.0, eps, sP,
                                        FR.location(td, tf, bd, bf), False, "pass", "complete", reason, "SUR"))
        return rows

    # ------------------------------------------------------------------------------------ evidencia demostrativa
    def contour_evidence(self, s, design, K1):
        from .contour import Evidence2D
        d = self.DESIGN[design]
        a, b = d * s.alpha, d * s.beta
        return Evidence2D(range=lambda x0, x1, y0, y1: a * _tt(x0, x1) + b * _tt(y0, y1) - K1,
                          dx=lambda x0, x1, y0, y1: a * (1 - 2 * Iv(x0, x1)), dy=lambda x0, x1, y0, y1: b * (1 - 2 * Iv(y0, y1)),
                          dxx=lambda *_: Iv.point(-2 * a), dyy=lambda *_: Iv.point(-2 * b),
                          fx=lambda x, y: a * (1 - 2 * x), fy=lambda x, y: b * (1 - 2 * y), source=SURROGATE_TAG)

    def path_evidence(self, s, design, section, rate, K1):
        from .raices import evidence_from_factors
        d = self.DESIGN[design]
        a, b = d * s.alpha, d * s.beta
        coeffs = {"tau_f_0": [-a, a, -K1], "tau_d_0": [-b, b, -K1], "paridad": [-(a + b), a + b, -K1],
                  "tau_d_estatutario": None if rate is None else [-b, b, a * rate * (1 - rate) - K1]}[section]
        return None if coeffs is None else evidence_from_factors([coeffs], source=SURROGATE_TAG)

    def c2_param_evidence(self, values, design, j, param, bd, bf):
        """C2 como función de phi (afín): encierro exacto y derivada constante."""
        if param != "phi":
            return None
        from .raices import evidence_from_factors
        d = self.DESIGN[design]
        md = _m(bd) if j in ("d", "df") else 0.0
        mf = _m(bf) if j in ("f", "df") else 0.0
        v0 = dict(values, phi=0.0)
        slope = d * (0.2 * md + 0.3 * mf)
        icpt = d * (self.alpha(v0) * md + self.beta(v0) * mf)
        return evidence_from_factors([[slope, icpt]], source=SURROGATE_TAG)

    def c2_struct_enclosure(self, box: dict, design, j, bd, bf, fixed=None):
        d = self.DESIGN[design]
        md = _m(bd) if j in ("d", "df") else 0.0
        mf = _m(bf) if j in ("f", "df") else 0.0
        return d * (self.alpha_iv(box) * md + self.beta_iv(box) * mf)

    def c2_exact(self, values, design, j, bd, bf):
        """Solo para pruebas independientes: forma cerrada de C2 del sustituto."""
        d = self.DESIGN[design]
        return d * (self.alpha(values) * (_m(bd) if j in ("d", "df") else 0.0) + self.beta(values) * (_m(bf) if j in ("f", "df") else 0.0))


def by_kind(kind: str):
    return {ModeloTeorico.kind: ModeloTeorico, ModeloTeoricoSinEncierros.kind: ModeloTeoricoSinEncierros,
            SURROGATE_TAG: SustitutoCertificado}[kind]()
