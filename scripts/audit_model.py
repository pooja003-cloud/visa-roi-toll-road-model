"""Audit the Visa toll-road model.

Checks
  1. Error values: no cached #DIV/0!, #REF!, #N/A, #VALUE!, #NAME? or #NUM! anywhere.
  2. Colour convention: hardcoded numbers are blue; formulas are never blue.
  3. Projection consistency: each projection row uses the same formula pattern
     across FY26P-FY30P (columns G-K), after normalising column letters.
  4. Independent recomputation of key historicals (FY21-FY25) from the Data tab:
     take rate, EBIT ex-litigation, FCF, invested capital, NOPAT, ROIC, shareholder yield.
  5. WACC recomputed by hand from the Tab 3 inputs.
  6. Projection identities: cash and invested-capital roll-forwards balance every year.

Not covered: the stress tests described in the README, which need a recalculation
engine (they were run with LibreOffice during development).

Usage:   python scripts/audit_model.py Visa_Toll_Road_Model.xlsx
Requires the workbook to carry cached values (i.e. last saved by Excel or LibreOffice).
Exit code 1 if any check fails.
"""
import re
import sys

from openpyxl import load_workbook

PATH = sys.argv[1] if len(sys.argv) > 1 else "Visa_Toll_Road_Model.xlsx"
wf = load_workbook(PATH)                    # formulas
wv = load_workbook(PATH, data_only=True)    # cached values
issues = []
ERRORS = ("#DIV/0!", "#REF!", "#N/A", "#VALUE!", "#NAME?", "#NUM!", "#NULL!")
PROJ = "GHIJK"


def labels(ws):
    return {ws.cell(i, 1).value: i for i in range(1, ws.max_row + 1) if ws.cell(i, 1).value}


# 1) error values
for ws in wv.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if isinstance(c.value, str) and c.value.strip() in ERRORS:
                issues.append(f"{ws.title}!{c.coordinate} shows {c.value}")

# 2) colour convention and 3) projection consistency
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for c in row:
            v = c.value
            # skip labels (A), notes (L) and the unit/source columns on the data tabs
            if v is None or c.column == 1 or c.column_letter == "L":
                continue
            if ws.title.startswith("Data") and c.column_letter in "BH":
                continue
            rgb = c.font.color.rgb if (c.font and c.font.color and c.font.color.type == "rgb") else ""
            is_blue = str(rgb).endswith("0000FF")
            if isinstance(v, (int, float)) and not isinstance(v, bool) and not is_blue:
                issues.append(f"{ws.title}!{c.coordinate} hardcode {v} is not blue")
            if isinstance(v, str) and v.startswith("=") and is_blue:
                issues.append(f"{ws.title}!{c.coordinate} formula is blue")

    if not ws.title.startswith("Tab"):
        continue
    for r in range(1, ws.max_row + 1):
        formulas = [ws[f"{col}{r}"].value for col in PROJ]
        if not all(isinstance(f, str) and f.startswith("=") for f in formulas):
            continue  # input rows, or rows populated in a single column only
        patterns = set()
        for col, f in zip(PROJ, formulas):
            prev = chr(ord(col) - 1)
            n = re.sub(r"(?<![A-Za-z$])" + col + r"(?=\$?\d)", "@C", f)
            n = re.sub(r"(?<![A-Za-z$])" + prev + r"(?=\$?\d)", "@P", n)
            patterns.add(n)
        if len(patterns) > 1:
            issues.append(f"{ws.title} row {r} ({ws.cell(r, 1).value}): projection formulas differ across FY26P-FY30P")

# 4) independent recomputation of historicals
d = wv["Data"]
LD = labels(d)


def dv(label, col):
    return d[f"{col}{LD[label]}"].value


def model(sheet, label, col):
    ws = wv[sheet]
    return ws[f"{col}{labels(ws)[label]}"].value


def invested_capital(col):
    debt = dv("Current maturities of debt", col) + dv("Long-term debt", col)
    cash = (dv("Cash and cash equivalents", col) + dv("Investment securities — current", col)
            + dv("Investment securities — non-current", col))
    return debt + dv("Total equity", col) - cash


checks = []
data_cols, model_cols = "CDEFG", "BCDEF"   # Data tab is shifted one column right
for i, (c, m) in enumerate(zip(data_cols, model_cols)):
    nr = dv("Net revenue (as reported)", c)
    ebit_x = dv("Operating income (as reported)", c) + dv("Litigation provision", c)
    tax = 0.17 if i == 0 else dv("Income tax provision", c) / dv("Income before income taxes", c)
    nopat = ebit_x * (1 - tax)
    ic = invested_capital(c)
    checks += [
        ("take rate bps", m, nr / (dv("Payments volume", c) * 1000) * 1e4, model("Tab1_Drivers", "Core take rate (bps)", m)),
        ("EBIT ex-lit", m, ebit_x, model("Tab2_Core_Returns", "EBIT ex-litigation (analytical)", m)),
        ("FCF", m, dv("Net cash from operating activities", c)
         - dv("Less: Purchases of property, equipment & technology", c), model("Tab2_Core_Returns", "Free cash flow (FCF)", m)),
        ("invested capital", m, ic, model("Tab2_Core_Returns", "Invested capital", m)),
        ("NOPAT", m, nopat, model("Tab3_ROIC_WACC", "NOPAT", m)),
        ("shareholder yield", m,
         (dv("Less: Dividends paid", c) + dv("Less: Repurchases of class A common stock", c))
         / (dv("Share price at FY-end close (unadjusted)", c) * dv("As-converted class A shares outstanding at FY-end", c)),
         model("Tab4_Capital_Allocation", "Shareholder yield", m)),
    ]
    if i:
        avg_ic = (ic + invested_capital(data_cols[i - 1])) / 2
        checks.append(("ROIC (avg capital)", m, nopat / avg_ic, model("Tab3_ROIC_WACC", "ROIC — on average capital (primary)", m)))
bad = [x for x in checks if abs(x[2] - x[3]) > 1e-6 * max(1, abs(x[2]))]
issues += [f"recompute mismatch: {name} {col}: expected {exp:.6f}, model {got:.6f}" for name, col, exp, got in bad]
print(f"Independent recompute: {len(checks)} checks, {len(bad)} mismatches")

# 5) WACC
t3 = wv["Tab3_ROIC_WACC"]
L3 = labels(t3)


def g(label):
    return t3[f"B{L3[label]}"].value


beta = g("Blume weight on raw beta") * g("Visa raw beta (5-year, monthly vs S&P 500)") + (1 - g("Blume weight on raw beta"))
ke = g("Risk-free rate (10-year U.S. Treasury par yield)") + beta * g("Equity risk premium")
equity = g("Share price ($) — close Oct 14, 2026") * g("As-converted class A shares outstanding (millions)")
debt = g("Total debt (Jun 30, 2026)")
kd = g("Pre-tax cost of debt (market)") * (1 - g("Tax rate"))
wacc = (equity * ke + debt * kd) / (equity + debt)
print(f"WACC recompute {wacc:.6f} vs model {g('WACC'):.6f}")
if abs(wacc - g("WACC")) > 1e-9:
    issues.append("WACC recompute mismatch")

# 6) projection roll-forward identities
t2, t4 = wv["Tab2_Core_Returns"], wv["Tab4_Capital_Allocation"]
L2, L4 = labels(t2), labels(t4)
for col in PROJ:
    prev = chr(ord(col) - 1)

    def v2(label, cc=col):
        return t2[f"{cc}{L2[label]}"].value

    returned = t4[f"{col}{L4['Total capital returned to shareholders']}"].value
    d_debt = v2("Total debt (short-term + long-term)") - v2("Total debt (short-term + long-term)", prev)
    exp_cash = v2("Free cash flow (FCF)") - returned - v2("Acquisitions (cash paid)") + d_debt
    act_cash = v2("Cash & cash equivalents") - v2("Cash & cash equivalents", prev)
    exp_ic = v2("Net income") - v2("Free cash flow (FCF)") + v2("Acquisitions (cash paid)")
    act_ic = v2("Invested capital") - v2("Invested capital", prev)
    if abs(act_cash - exp_cash) > 0.01 or abs(act_ic - exp_ic) > 0.01:
        issues.append(f"{col}: roll-forward mismatch (cash {act_cash:.1f} vs {exp_cash:.1f}; IC {act_ic:.1f} vs {exp_ic:.1f})")
print("Roll-forward identities checked for FY26P-FY30P")

print("\n".join(issues) if issues else "All checks passed")
sys.exit(1 if issues else 0)
