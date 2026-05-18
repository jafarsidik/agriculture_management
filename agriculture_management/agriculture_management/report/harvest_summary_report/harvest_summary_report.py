# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe
from frappe import _


def execute(filters: dict | None = None):
	"""Return columns and data for the report.

	This is the main entry point for the report. It accepts the filters as a
	dictionary and should return columns and data. It is called by the framework
	every time the report is refreshed or a filter is updated.
	"""
	filters = filters or {}		
	columns = get_columns()
	data = get_data(filters)

	return columns, data
		
		
def get_columns():		
	return [		
		{"label": _("Harvest ID"),        "fieldname": "name",              "fieldtype": "Link",     "options": "Harvest Record", "width": 140},		
		{"label": _("Farm"),              "fieldname": "farm",              "fieldtype": "Link",     "options": "Farm",           "width": 160},		
		{"label": _("Plot"),              "fieldname": "farm_plot",         "fieldtype": "Link",     "options": "Farm Plot",      "width": 160},		
		{"label": _("Crop"),              "fieldname": "crop",              "fieldtype": "Link",     "options": "Crop",           "width": 140},		
		{"label": _("Season"),            "fieldname": "season",            "fieldtype": "Link",     "options": "Crop Season",    "width": 160},		
		{"label": _("Planting Date"),     "fieldname": "planting_date",     "fieldtype": "Date",                                  "width": 110},		
		{"label": _("Harvest Date"),      "fieldname": "harvest_date",      "fieldtype": "Date",                                  "width": 110},		
		{"label": _("Est. Yield"),        "fieldname": "estimated_yield",   "fieldtype": "Float",                                 "width": 110},		
		{"label": _("Actual Yield"),      "fieldname": "total_net_weight",  "fieldtype": "Float",                                 "width": 110},		
		{"label": _("Variance (%)"),      "fieldname": "yield_variance",    "fieldtype": "Float",                                 "width": 100},		
		{"label": _("Unit"),              "fieldname": "yield_unit",        "fieldtype": "Data",                                  "width":  70},		
		{"label": _("Grade"),             "fieldname": "grade",             "fieldtype": "Data",                                  "width": 100},		
		{"label": _("Grade Net Wt"),      "fieldname": "grade_net_weight",  "fieldtype": "Float",                                 "width": 110},		
		{"label": _("Market Price"),      "fieldname": "market_price",      "fieldtype": "Currency",                              "width": 110},		
		{"label": _("Total Value"),       "fieldname": "total_value",       "fieldtype": "Currency",                              "width": 120},		
		{"label": _("Status"),            "fieldname": "status",            "fieldtype": "Data",                                  "width":  90},		
	]		
		
		
def get_data(filters):		
	conditions = _build_conditions(filters)		
		
	# Main harvest records		
	records = frappe.db.sql("""		
		SELECT		
			hr.name,		
			hr.farm,		
			hr.farm_plot,		
			hr.crop,		
			hr.season,		
			pr.planting_date,		
			hr.harvest_date,		
			hr.estimated_yield,		
			hr.total_net_weight,		
			hr.yield_variance,		
			hr.yield_unit,		
			hr.status		
		FROM `tabHarvest Record` hr		
		LEFT JOIN `tabPlanting Record` pr ON hr.planting_record = pr.name		
		WHERE hr.docstatus = 1		
		{conditions}		
		ORDER BY hr.harvest_date DESC		
	""", filters, as_dict=True)		
		
	# Fetch harvest lines per record		
	result = []		
	for rec in records:		
		lines = frappe.db.get_all(		
			"Harvest Line",		
			filters={"parent": rec.name},		
			fields=["grade", "net_weight", "market_price", "total_value"],		
			order_by="grade"		
		)		
		if lines:		
			for i, line in enumerate(lines):		
				row = rec.copy() if i == 0 else {		
					"name": "", "farm": "", "farm_plot": "", "crop": "",		
					"season": "", "planting_date": "", "harvest_date": "",		
					"estimated_yield": "", "total_net_weight": "",		
					"yield_variance": "", "yield_unit": "", "status": ""		
				}		
				row["grade"]           = line.grade		
				row["grade_net_weight"]= line.net_weight		
				row["market_price"]    = line.market_price		
				row["total_value"]     = line.total_value		
				result.append(row)		
		else:		
			rec["grade"] = rec["grade_net_weight"] = rec["market_price"] = rec["total_value"] = ""		
			result.append(rec)		
		
	return result		
		
		
def _build_conditions(filters):		
	cond = []		
	if filters.get("farm"):        cond.append("hr.farm = %(farm)s")		
	if filters.get("season"):      cond.append("hr.season = %(season)s")		
	if filters.get("crop"):        cond.append("hr.crop = %(crop)s")		
	if filters.get("farm_plot"):   cond.append("hr.farm_plot = %(farm_plot)s")		
	if filters.get("from_date"):   cond.append("hr.harvest_date >= %(from_date)s")		
	if filters.get("to_date"):     cond.append("hr.harvest_date <= %(to_date)s")		
	if filters.get("status"):      cond.append("hr.status = %(status)s")		
	return ("AND " + " AND ".join(cond)) if cond else ""		
		
