// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.query_reports["Crop Yield Analysis"] = {
	filters: [
		{"fieldname": "farm",      "label": "Farm",       "fieldtype": "Link",   "options": "Farm"},		
		{"fieldname": "season",    "label": "Season",     "fieldtype": "Link",   "options": "Crop Season"},		
		{"fieldname": "crop",      "label": "Crop",       "fieldtype": "Link",   "options": "Crop"},		
		{"fieldname": "farm_plot", "label": "Farm Plot",  "fieldtype": "Link",   "options": "Farm Plot"},		
		{"fieldname": "from_date", "label": "From Date",  "fieldtype": "Date"},		
		{"fieldname": "to_date",   "label": "To Date",    "fieldtype": "Date"},		
		{"fieldname": "status",    "label": "Status",     "fieldtype": "Select", "options": "\nDraft\nSubmitted\nAvailable\nSold\nWaste"}		

	],
};
