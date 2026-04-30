# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe		
from frappe import _		
from frappe.model.document import Document		



class FarmSalesOrder(Document):
			
    def validate(self):		
        self._calc_sales_lines()		
        self._calc_grand_total()		
		
    def _calc_sales_lines(self):		
        """Auto-fill crop from Harvest Record, calc line totals"""		
        for line in self.get("sales_lines") or []:		
            # Auto-fill crop from Harvest Record		
            if line.harvest_record and not line.crop:		
                line.crop = frappe.db.get_value(		
                    "Harvest Record", line.harvest_record, "crop"		
                )		
            line.total = (line.quantity or 0) * (line.unit_price or 0)		
		
    def _calc_grand_total(self):		
        subtotal = sum((l.total or 0) for l in (self.get("sales_lines") or []))		
        self.subtotal       = subtotal		
        self.discount_amount = (subtotal * (self.discount_pct or 0) / 100) if hasattr(self, "discount_pct") else (self.discount or 0)		
        self.grand_total    = subtotal - (self.discount or 0) + (self.tax or 0)		
		
    # ── On Submit ────────────────────────────────────────────		
    def on_submit(self):		
        self._update_harvest_status()		
		
    def _update_harvest_status(self):		
        """Mark linked Harvest Records as Sold"""		
        sold_records = set()		
        for line in self.get("sales_lines") or []:		
            if line.harvest_record and line.harvest_record not in sold_records:		
                frappe.db.set_value("Harvest Record", line.harvest_record, "status", "Sold")		
                sold_records.add(line.harvest_record)		
		
    # ── On Cancel ────────────────────────────────────────────		
    def on_cancel(self):		
        """Revert Harvest Record status to Available on cancel"""		
        reverted = set()		
        for line in self.get("sales_lines") or []:		
            if line.harvest_record and line.harvest_record not in reverted:		
                frappe.db.set_value("Harvest Record", line.harvest_record, "status", "Available")		
                reverted.add(line.harvest_record)		
		

