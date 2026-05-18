# ============================================================		
#  Farm Profitability Report		
#  Type   : Script Report		
#  DocType: Farm Cost Sheet		
#  File   : farm_profitability_report.py		
# ============================================================		
import frappe		
from frappe import _		
		
		
def execute(filters=None):		
    filters = filters or {}		
    columns = get_columns()		
    data, chart = get_data(filters)		
    return columns, data, None, chart		
		
		
def get_columns():		
    return [		
        {"label": _("Season"),           "fieldname": "season",          "fieldtype": "Link",    "options": "Crop Season", "width": 170},		
        {"label": _("Farm"),             "fieldname": "farm",            "fieldtype": "Link",    "options": "Farm",        "width": 160},		
        {"label": _("Crop"),             "fieldname": "crop",            "fieldtype": "Link",    "options": "Crop",        "width": 140},		
        {"label": _("Area (Ha)"),        "fieldname": "total_area",      "fieldtype": "Float",                             "width":  90},		
        {"label": _("Revenue"),          "fieldname": "total_revenue",   "fieldtype": "Currency",                          "width": 130},		
        {"label": _("Labor Cost"),       "fieldname": "labor_cost",      "fieldtype": "Currency",                          "width": 120},		
        {"label": _("Input Cost"),       "fieldname": "input_cost",      "fieldtype": "Currency",                          "width": 120},		
        {"label": _("Equipment Cost"),   "fieldname": "equipment_cost",  "fieldtype": "Currency",                          "width": 120},		
        {"label": _("Maintenance Cost"), "fieldname": "maintenance_cost","fieldtype": "Currency",                          "width": 120},		
        {"label": _("Overhead"),         "fieldname": "overhead_cost",   "fieldtype": "Currency",                          "width": 110},		
        {"label": _("Total Cost"),       "fieldname": "total_cost",      "fieldtype": "Currency",                          "width": 120},		
        {"label": _("Gross Profit"),     "fieldname": "gross_profit",    "fieldtype": "Currency",                          "width": 120},		
        {"label": _("Margin (%)"),       "fieldname": "profit_margin",   "fieldtype": "Float",                             "width":  90},		
        {"label": _("ROI (%)"),          "fieldname": "roi",             "fieldtype": "Float",                             "width":  80},		
        {"label": _("Cost / Ha"),        "fieldname": "cost_per_ha",     "fieldtype": "Currency",                          "width": 110},		
        {"label": _("Revenue / Ha"),     "fieldname": "revenue_per_ha",  "fieldtype": "Currency",                          "width": 110},		
    ]		
		
		
def get_data(filters):		
    conditions = _build_conditions(filters)		
		
    rows = frappe.db.sql(f"""		
        SELECT		
            fcs.season,		
            fcs.farm,		
            fcs.crop,		
            fcs.total_area,		
            fcs.total_revenue,		
            fcs.labor_cost,		
            fcs.input_cost,		
            fcs.equipment_cost,		
            fcs.maintenance_cost,		
            fcs.overhead_cost,		
            fcs.total_cost,		
            fcs.gross_profit,		
            fcs.profit_margin,		
            fcs.roi,		
            fcs.cost_per_ha		
        FROM `tabFarm Cost Sheet` fcs		
        WHERE fcs.docstatus = 1		
        {conditions}		
        ORDER BY fcs.season, fcs.farm		
    """, filters, as_dict=True)		
		
    for r in rows:		
        area = r.total_area or 1		
        r.revenue_per_ha = round((r.total_revenue or 0) / area, 2)		
		
    # Chart: Grouped bar — Revenue vs Total Cost per Season+Farm		
    labels  = [f"{r.farm} / {r.crop}" for r in rows]		
    revenue = [r.total_revenue or 0 for r in rows]		
    cost    = [r.total_cost or 0    for r in rows]		
    profit  = [r.gross_profit or 0  for r in rows]		
		
    chart = {		
        "data": {		
            "labels": labels,		
            "datasets": [		
                {"name": _("Revenue"),     "values": revenue},		
                {"name": _("Total Cost"),  "values": cost},		
                {"name": _("Gross Profit"),"values": profit},		
            ]		
        },		
        "type":   "bar",		
        "colors": ["#2E7D32", "#E65100", "#1565C0"],		
        "height": 300,		
        "barOptions": {"stacked": False}		
    }		
		
    return rows, chart		
		
		
def _build_conditions(filters):		
    cond = []		
    if filters.get("farm"):   cond.append("fcs.farm = %(farm)s")		
    if filters.get("season"): cond.append("fcs.season = %(season)s")		
    if filters.get("crop"):   cond.append("fcs.crop = %(crop)s")		
    return ("AND " + " AND ".join(cond)) if cond else ""		
		
