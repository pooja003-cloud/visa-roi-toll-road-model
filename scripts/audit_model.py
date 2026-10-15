"""Audit the Visa toll-road model: colour conventions, projection-formula consistency,
independent recomputation of key historicals, WACC, and projection roll-forward identities.
Usage: python scripts/audit_model.py Visa_Toll_Road_Model.xlsx
Requires the workbook to have cached values (i.e. last saved by Excel or LibreOffice)."""
import re, sys
from openpyxl import load_workbook
P=sys.argv[1] if len(sys.argv)>1 else "Visa_Toll_Road_Model.xlsx"
wf=load_workbook(P); wv=load_workbook(P,data_only=True)
issues=[]
def lab(ws): return {ws.cell(i,1).value:i for i in range(1,ws.max_row+1) if ws.cell(i,1).value}
# 1) Font-colour convention + formula consistency
for ws in wf.worksheets:
    for row in ws.iter_rows():
        for c in row:
            v=c.value
            if v is None or c.column==1 or c.column_letter=="L" or (ws.title=="Data" and c.column_letter in "BH"): continue
            col=(c.font.color.rgb if c.font and c.font.color and c.font.color.type=="rgb" else None) or "auto"
            if isinstance(v,(int,float)) and not col.endswith("0000FF"):
                issues.append(f"{ws.title}!{c.coordinate} hardcode {v} not blue ({col})")
            if isinstance(v,str) and v.startswith("="):
                xsheet="!" in v
                if col.endswith("0000FF"): issues.append(f"{ws.title}!{c.coordinate} formula in blue")
    # projection row consistency: G..K formulas should be the same after normalising column letters
    if ws.title.startswith("Tab") and ws.title!="Tab3_ROIC_WACC" or ws.title=="Tab3_ROIC_WACC":
        for r in range(1,ws.max_row+1):
            fs=[ws[f"{c}{r}"].value for c in "HIJK"]
            if all(isinstance(x,str) and x.startswith("=") for x in fs):
                norm=[]
                for i,f in enumerate(fs):
                    cur="HIJK"[i]; pr=chr(ord(cur)-1)
                    n=re.sub(r"(?<![A-Za-z$])"+cur+r"(?=\$?\d)","@C",f)
                    n=re.sub(r"(?<![A-Za-z$])"+pr+r"(?=\$?\d)","@P",n)
                    norm.append(n)
                if len(set(norm))>1: issues.append(f"{ws.title} row {r} ({ws.cell(r,1).value}): inconsistent projection formulas {fs}")
# 2) Independent recomputation of key historicals from Data values
d=wv["Data"]; L=lab(d)
def dv(label,col): return d[f"{col}{L[label]}"].value
cols="CDEFG"
def T(sheet,label,col): ws=wv[sheet]; return ws[f"{col}{lab(ws)[label]}"].value
chk=[]
for i,c in enumerate(cols):
    tc="BCDEF"[i]
    nr=dv("Net revenue (as reported)",c); pv=dv("Payments volume",c)
    chk.append(("take bps",tc,nr/(pv*1000)*1e4,T("Tab1_Drivers","Core take rate (bps)",tc)))
    ebit=dv("Operating income (as reported)",c); lit=dv("Litigation provision",c)
    chk.append(("EBIT ex-lit",tc,ebit+lit,T("Tab2_Core_Returns","EBIT ex-litigation (analytical)",tc)))
    fcf=dv("Net cash from operating activities",c)-dv("Less: Purchases of property, equipment & technology",c)
    chk.append(("FCF",tc,fcf,T("Tab2_Core_Returns","Free cash flow (FCF)",tc)))
    debt=dv("Current maturities of debt",c)+dv("Long-term debt",c)
    cash=dv("Cash and cash equivalents",c)+dv("Investment securities — current",c)+dv("Investment securities — non-current",c)
    ic=debt+dv("Total equity",c)-cash
    chk.append(("IC",tc,ic,T("Tab2_Core_Returns","Invested capital",tc)))
    tax=dv("Income tax provision",c)/dv("Income before income taxes",c) if i else 0.17
    nopat=(ebit+lit)*(1-tax)
    chk.append(("NOPAT",tc,nopat,T("Tab3_ROIC_WACC","NOPAT",tc)))
    mc=dv("Share price at FY-end close (unadjusted)",c)*dv("As-converted class A shares outstanding at FY-end",c)
    ret=dv("Less: Dividends paid",c)+dv("Less: Repurchases of class A common stock",c)
    chk.append(("Sh. yield",tc,ret/mc,T("Tab4_Capital_Allocation","Shareholder yield",tc)))
    if i:
        pc=cols[i-1]
        icp=dv("Current maturities of debt",pc)+dv("Long-term debt",pc)+dv("Total equity",pc)-(dv("Cash and cash equivalents",pc)+dv("Investment securities — current",pc)+dv("Investment securities — non-current",pc))
        chk.append(("ROIC avg",tc,nopat/((ic+icp)/2),T("Tab3_ROIC_WACC","ROIC — on average capital (primary)",tc)))
bad=[x for x in chk if abs(x[2]-x[3])>1e-6*max(1,abs(x[2]))]
print("Independent recompute:",len(chk),"checks,",len(bad),"mismatches", bad)
# 3) WACC recompute
t3=wv["Tab3_ROIC_WACC"]; L3=lab(t3); g=lambda l: t3[f"B{L3[l]}"].value
beta=0.67*g("Visa raw beta (5-year, monthly vs S&P 500)")+0.33
ke=g("Risk-free rate (10-year U.S. Treasury par yield)")+beta*g("Equity risk premium")
mc=g("Share price ($) — close Oct 14, 2026")*g("As-converted class A shares outstanding (millions)"); dbt=g("Total debt (Jun 30, 2026)")
kd=g("Visa 4.150% senior notes due Dec 14, 2035 — yield (CUSIP 92826CAE2)")*(1-g("Tax rate"))
w=(mc*ke+dbt*kd)/(mc+dbt); print("WACC recompute",round(w,6),"model",round(g("WACC"),6))
# 4) Projection identities
t2=wv["Tab2_Core_Returns"]; L2=lab(t2); t4=wv["Tab4_Capital_Allocation"]; L4=lab(t4)
for c in "GHIJK":
    p=chr(ord(c)-1); V=lambda ws,L,l,cc=c: ws[f"{cc}{L[l]}"].value
    dcash=V(t2,L2,"Cash & cash equivalents")-V(t2,L2,"Cash & cash equivalents",p)
    exp=V(t2,L2,"Free cash flow (FCF)")-V(t4,L4,"Total capital returned to shareholders")-V(t2,L2,"Acquisitions (cash paid)")+V(t2,L2,"Total debt (short-term + long-term)")-V(t2,L2,"Total debt (short-term + long-term)",p)
    dic=V(t2,L2,"Invested capital")-V(t2,L2,"Invested capital",p); exp_ic=V(t2,L2,"Net income")-V(t2,L2,"Free cash flow (FCF)")+V(t2,L2,"Acquisitions (cash paid)")
    if abs(dcash-exp)>0.01 or abs(dic-exp_ic)>0.01: issues.append(f"{c}: cash/IC roll-forward mismatch {dcash:.1f} vs {exp:.1f}; {dic:.1f} vs {exp_ic:.1f}")
print("Roll-forward identities checked G–K")
print("\n".join(issues) if issues else "No convention/consistency issues")
