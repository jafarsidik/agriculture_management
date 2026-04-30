# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe		
from frappe import _		
from frappe.model.document import Document		



class FarmActivity(Document):
	# ── Validate ─────────────────────────────────────────────		
    def validate(self):		
        self._calc_duration()		
        self._calc_labor_cost()		
        self._calc_input_cost()		
        self._calc_equipment_cost()		
        self._calc_total_cost()		
		
    def _calc_duration(self):		
        """Duration in hours from start_time and end_time (HH:MM strings)"""		
        if self.start_time and self.end_time:		
            try:		
                sh, sm = map(int, self.start_time.split(":"))		
                eh, em = map(int, self.end_time.split(":"))		
                minutes = (eh * 60 + em) - (sh * 60 + sm)		
                if minutes > 0:		
                    self.duration_hours = round(minutes / 60, 2)		
            except Exception:		
                pass		
		
    def _calc_labor_cost(self):		
        """Sum total_wage from all Activity Worker child rows"""		
        total = 0		
        for w in self.get("workers") or []:		
            overtime = (w.overtime_hours or 0) * (w.overtime_rate or w.wage_rate or 0)		
            base      = (w.hours_worked or 0) * (w.wage_rate or 0)		
            w.total_wage = base + overtime		
            total += w.total_wage		
        self.total_labor_cost = total		
		
    def _calc_input_cost(self):		
        """Sum total_amount from all Activity Input child rows"""		
        total = 0		
        for inp in self.get("inputs_used") or []:		
            inp.total_amount = (inp.quantity or 0) * (inp.rate or 0)		
            total += inp.total_amount		
        self.total_input_cost = total		
		
    def _calc_equipment_cost(self):		
        """Sum usage_cost from all Activity Equipment child rows"""		
        total = 0		
        for eq in self.get("equipment_used") or []:		
            # usage_cost may be manually entered or auto-calc'd from depreciation		
            total += (eq.usage_cost or 0)		
            # Auto-fill fuel_cost if not set		
            if eq.fuel_used and not eq.fuel_cost:		
                eq.fuel_cost = eq.fuel_used * 1.0   # default $1/L; adjust per settings		
        self.total_equip_cost = total		
		
    def _calc_total_cost(self):		
        self.total_cost = (		
            (self.total_labor_cost or 0)		
            + (self.total_input_cost or 0)		
            + (self.total_equip_cost or 0)		
        )		
		
    # ── On Submit: deduct stock ──────────────────────────────		
    def on_submit(self):		
        self._deduct_input_stock()		
        self._update_equipment_usage_hours()		
		
    def _deduct_input_stock(self):		
        """Create an Input Stock Record (Out) for each input used"""		
        for inp in self.get("inputs_used") or []:		
            if not inp.input_item or not inp.quantity:		
                continue		
		
            # Validate stock balance first		
            balance = frappe.db.get_value(		
                "Input Stock Balance",		
                {"farm": self.farm, "input_item": inp.input_item},		
                "current_stock"		
            ) or 0		
		
            if balance < inp.quantity:		
                frappe.throw(		
                    _("Insufficient stock for <b>{0}</b>. "		
                      "Available: {1}, Required: {2}").format(		
                        inp.input_item, balance, inp.quantity		
                    )		
                )		
		
            # Create stock record		
            stock_rec = frappe.new_doc("Input Stock Record")		
            stock_rec.update({		
                "transaction_type": "Out (Activity)",		
                "transaction_date": self.activity_date,		
                "farm":             self.farm,		
                "input_item":       inp.input_item,		
                "quantity":         inp.quantity,		
                "unit":             inp.unit,		
                "unit_price":       inp.rate,		
                "total_value":      inp.total_amount,		
                "ref_doctype":      "Farm Activity",		
                "ref_name":         self.name,		
                "batch_no":         inp.batch_no,		
            })		
            stock_rec.insert(ignore_permissions=True)		
            stock_rec.submit()		
		
    def _update_equipment_usage_hours(self):		
        """Add usage_hours to Farm Equipment.total_usage_hours"""		
        for eq in self.get("equipment_used") or []:		
            if not eq.equipment or not eq.usage_hours:		
                continue		
            frappe.db.set_value(		
                "Farm Equipment", eq.equipment,		
                "total_usage_hours",		
                (frappe.db.get_value("Farm Equipment", eq.equipment, "total_usage_hours") or 0)		
                + eq.usage_hours		
            )		
		
    # ── On Cancel: reverse stock ─────────────────────────────		
    def on_cancel(self):		
        """Cancel all related Input Stock Records"""		
        stock_records = frappe.get_all(		
            "Input Stock Record",		
            filters={"ref_doctype": "Farm Activity", "ref_name": self.name, "docstatus": 1},		
            pluck="name"		
        )		
        for sr in stock_records:		
            doc = frappe.get_doc("Input Stock Record", sr)		
            doc.cancel()		

