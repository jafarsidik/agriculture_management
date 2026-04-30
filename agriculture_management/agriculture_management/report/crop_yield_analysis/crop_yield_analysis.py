# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt
import frappe		
from frappe import _		
		
		
def execute(filters=None):		
	filters = filters or {}		
	columns = get_columns()		
	data    = get_data(filters)
	chart	= grafik(filters)		
	return columns, data,None, chart		
		

def get_columns():		
	return [		
		{"label": _("Crop"),              "fieldname": "crop",             "fieldtype": "Link",    "options": "Crop",        "width": 160},		
		{"label": _("Season"),            "fieldname": "season",           "fieldtype": "Link",    "options": "Crop Season", "width": 160},		
		{"label": _("Farm"),              "fieldname": "farm",             "fieldtype": "Link",    "options": "Farm",        "width": 160},		
		{"label": _("Plot"),              "fieldname": "farm_plot",        "fieldtype": "Link",    "options": "Farm Plot",   "width": 150},		
		{"label": _("Area (Ha)"),         "fieldname": "area_planted",     "fieldtype": "Float",                             "width":  90},		
		{"label": _("Est. Yield"),        "fieldname": "total_est_yield",  "fieldtype": "Float",                             "width": 110},		
		{"label": _("Actual Yield"),      "fieldname": "total_net_weight", "fieldtype": "Float",                             "width": 110},		
		{"label": _("Yield / Ha"),        "fieldname": "yield_per_ha",     "fieldtype": "Float",                             "width": 100},		
		{"label": _("Unit"),              "fieldname": "yield_unit",       "fieldtype": "Data",                              "width":  70},		
		{"label": _("Variance (%)"),      "fieldname": "avg_variance",     "fieldtype": "Float",                             "width": 100},		
		{"label": _("Total Revenue"),     "fieldname": "total_revenue",    "fieldtype": "Currency",                          "width": 130},		
		{"label": _("Revenue / Ha"),      "fieldname": "revenue_per_ha",   "fieldtype": "Currency",                          "width": 120},		
		{"label": _("Harvest Count"),     "fieldname": "harvest_count",    "fieldtype": "Int",                               "width":  90},		
	]		
		
		
def get_data(filters):		
	conditions = _build_conditions(filters)		
		
	rows = frappe.db.sql(f"""		
		SELECT		
			hr.crop as crop,		
			hr.season,		
			hr.farm,		
			hr.farm_plot,		
			pr.yield_unit,		
			SUM(pr.area_planted)     AS area_planted,		
			SUM(hr.estimated_yield)  AS total_est_yield,		
			SUM(hr.total_net_weight) AS total_net_weight,		
			AVG(hr.yield_variance)   AS avg_variance,		
			SUM(hr.total_value)      AS total_revenue,		
			COUNT(hr.name)           AS harvest_count		
		FROM `tabHarvest Record` hr		
		LEFT JOIN `tabPlanting Record` pr ON hr.planting_record = pr.name		
		WHERE hr.docstatus = 1		
		{conditions}		
		GROUP BY hr.crop, hr.season, hr.farm, hr.farm_plot		
		ORDER BY hr.crop, hr.season		
	""", filters, as_dict=True)		
		
	for r in rows:		
		area = r.area_planted or 1		
		r.yield_per_ha  = round((r.total_net_weight or 0) / area, 2)		
		r.revenue_per_ha= round((r.total_revenue or 0) / area, 2)		
		r.avg_variance  = round(r.avg_variance or 0, 2)		
		
	return rows		
		
def grafik(filters):
    conditions = _build_conditions(filters)

    rows = frappe.db.sql(f"""
        SELECT
            hr.crop,
            SUM(hr.estimated_yield)  AS total_est_yield,
            SUM(hr.total_net_weight) AS total_net_weight,
            SUM(hr.total_value)      AS total_revenue
        FROM `tabHarvest Record` hr
        LEFT JOIN `tabPlanting Record` pr ON hr.planting_record = pr.name
        WHERE hr.docstatus = 1
        {conditions}
        GROUP BY hr.crop
        ORDER BY hr.crop
    """, filters, as_dict=True)

    if not rows:
        return None

    labels  = [r.crop for r in rows]
    est     = [round(r.total_est_yield  or 0, 2) for r in rows]
    actual  = [round(r.total_net_weight or 0, 2) for r in rows]
    revenue = [round((r.total_revenue   or 0) / 1_000_000, 2) for r in rows]

    chart = {
        "data": {
            "labels": labels,
            "datasets": [
                {"name": "Est. Yield",     "values": est,     "chartType": "bar"},
                {"name": "Actual Yield",   "values": actual,  "chartType": "bar"},
                {"name": "Revenue (Juta)", "values": revenue, "chartType": "line"},
            ],
        },
        "type": "axis-mixed",
        "colors": ["#5e64ff", "#28a745", "#ff6b35"],
        "axisOptions": {
            "xIsSeries": True,
        },
        "height": 300,
    }

    return chart

def _build_conditions(filters):		
	cond = []		
	if filters.get("farm"):      cond.append("hr.farm = %(farm)s")		
	if filters.get("season"):    cond.append("hr.season = %(season)s")		
	if filters.get("crop"):      cond.append("hr.crop_ = %(crop)s")		
	if filters.get("from_date"): cond.append("hr.harvest_date >= %(from_date)s")		
	if filters.get("to_date"):   cond.append("hr.harvest_date <= %(to_date)s")		
	return ("AND " + " AND ".join(cond)) if cond else ""


