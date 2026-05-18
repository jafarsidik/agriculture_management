// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.query_reports["Farm Profitability"] = {
	filters: [
		{"fieldname": "farm",      "label": "Farm",       "fieldtype": "Link",   "options": "Farm"},		
		{"fieldname": "season",    "label": "Season",     "fieldtype": "Link",   "options": "Crop Season"},		
		{"fieldname": "crop",      "label": "Crop",       "fieldtype": "Link",   "options": "Crop"}
	],
};
