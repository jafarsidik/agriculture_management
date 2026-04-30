# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe		
from frappe import _		
from frappe.model.document import Document		


class FarmPurchaseOrder(Document):
			
    def validate(self):		
        self._calc_lines()		
        self._calc_grand_total()		
		
    def _calc_lines(self):		
        for line in self.get("po_lines") or []:		
            line.amount = (line.quantity or 0) * (line.unit_price or 0)		
		
    def _calc_grand_total(self):		
        self.subtotal    = sum((l.amount or 0) for l in (self.get("po_lines") or []))		
        self.grand_total = self.subtotal - (self.discount or 0) + (self.tax or 0)		
		
    # ── On Submit: create Input Stock Records (In) ───────────		
    def on_submit(self):		
        for line in self.get("po_lines") or []:		
            if not line.input_item or not line.quantity:		
                continue		
            stock_rec = frappe.new_doc("Input Stock Record")		
            stock_rec.update({		
                "transaction_type": "In (Purchase)",		
                "transaction_date": self.order_date,		
                "farm":             self.farm,		
                "input_item":       line.input_item,		
                "quantity":         line.quantity,		
                "unit":             line.unit,		
                "unit_price":       line.unit_price,		
                "total_value":      line.amount,		
                "ref_doctype":      "Farm Purchase Order",		
                "ref_name":         self.name,		
                "expiry_date":      line.expiry_date,		
            })		
            stock_rec.insert(ignore_permissions=True)		
            stock_rec.submit()		
		
        frappe.msgprint(		
            _("Stock records created for all {0} items.").format(		
                len(self.get("po_lines") or [])		
            ),		
            alert=True, indicator="green"		
        )		
        frappe.db.set_value("Farm Purchase Order", self.name, "status", "Received")		
		
    # ── On Cancel ────────────────────────────────────────────		
    def on_cancel(self):		
        """Cancel related Input Stock Records"""		
        records = frappe.get_all(		
            "Input Stock Record",		
            filters={"ref_doctype": "Farm Purchase Order", "ref_name": self.name, "docstatus": 1},		
            pluck="name"		
        )		
        for r in records:		
            frappe.get_doc("Input Stock Record", r).cancel()		
		

