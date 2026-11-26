# Rate caps and the cost of formal adoption

Section 5.1 asks how much withholding adds when the domestic tax is available. Table 2 compares the three instrument menus under a domestic cap of 35% and withholding caps of 15% and 30%. For each menu the structural point is held fixed at its favorable base value and the tax rates are optimized again.

The [Table 2 example](../README.md#reproduce-table-2) gives the command. Use `table3.csv` for the displayed cells and `summary.json` for the underlying intervals.

### Comparing tax menus

The four combined-menu rows cross the two domestic designs (gross and net) with the two withholding caps. Each row is evaluated under linear incidence (E11) and statutory gross-up. The single-instrument columns use their respective favorable witnesses. With zero withholding, both incidence rules give the same domestic-only ceiling. At the withholding-only witnesses the buyer bears the whole tax under either rule. Appendix Tables S7 and S8 report interval bounds for the combined menu and for the domestic share.

### Locating the adoption threshold

At the original 60% caps, the statutory gross design has a certified revenue supremum of 0.7821. A numerical diagnostic places the formal-adoption threshold near a domestic rate of 0.588 when withholding is 60%. Whether a rate pair attains the supremum remains open. In the net design the statutory ceiling is 0.5518 and is attained at the caps. The lower-cap exercise reports the adoption margin at the caps and locates the gross threshold beyond the domestic cap.

`calculo.py` calls the model’s ceiling certifier, `testigos_propios.py` evaluates the single-instrument witnesses, and the two `diagnostico_*.py` scripts locate the thresholds. The statutory rule and its treatment of concealment costs are described in [the model note](VARIANTE_ESTATUTARIA.md).
