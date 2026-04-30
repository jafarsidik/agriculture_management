# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe		
from frappe import _		
from frappe.utils import add_days		
from frappe.model.document import Document		



class EquipmentMaintenance(Document):
			
    def validate(self):		
        self._calc_parts_cost()		
        self._calc_total_cost()		
		
    def _calc_parts_cost(self):		
        """Sum total from Maintenance Part child rows"""		
        total = 0		
        for part in self.get("parts_used") or []:		
            part.total = (part.quantity or 0) * (part.unit_price or 0)		
            total += part.total		
        self.parts_cost = total		
		
    def _calc_total_cost(self):		
        self.maintenance_cost = (self.labor_cost or 0) + (self.parts_cost or 0)		
		
    # ── On Submit ────────────────────────────────────────────		
    def on_submit(self):		
        self._set_equipment_status("Maintenance")		
		
    def _set_equipment_status(self, status):		
        if not self.equipment:		
            return		
        update = {"status": status}		
		
        # When completing maintenance → update next_maintenance date		
        if status == "Available" and self.next_maintenance:		
            update["next_maintenance"] = self.next_maintenance		
		
        frappe.db.set_value("Farm Equipment", self.equipment, update)		
        frappe.msgprint(		
            _("Farm Equipment <b>{0}</b> status → <b>{1}</b>.").format(		
                self.equipment, status		
            ),		
            alert=True, indicator="blue"		
        )		
		
    # ── Mark Complete (custom button) ────────────────────────		
    @frappe.whitelist()		
    def mark_complete(self):		
        """		
        Called from a custom button on the form.		
        Sets status to Completed and returns equipment to Available.		
        """		
        if self.docstatus != 1:		
            frappe.throw(_("Document must be submitted before marking complete."))		
        if self.status == "Completed":		
            frappe.throw(_("Already marked as Completed."))		
		
        self.db_set("status", "Completed")		
        if not self.completion_date:		
            self.db_set("completion_date", frappe.utils.today())		
		
        self._set_equipment_status("Available")		
        return _("Maintenance marked as Completed.")		
		
    # ── On Cancel ────────────────────────────────────────────		
    def on_cancel(self):		
        self._set_equipment_status("Available")		
		

