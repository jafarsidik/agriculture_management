# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe		
from frappe import _		
from frappe.utils import add_days, getdate, today		
from frappe.model.document import Document		



class PlantingRecord(Document):
	# ── Validate ─────────────────────────────────────────────		
    def validate(self):		
        self._set_expected_harvest()		
        self._validate_plot_availability()		
        self._validate_area()		
		
    def _set_expected_harvest(self):		
        """Auto-fill expected_harvest = planting_date + crop.growth_duration"""		
        if self.planting_date and self.crop:		
            growth_days = frappe.db.get_value("Crop", self.crop, "growth_duration")		
            if growth_days:		
                self.expected_harvest = add_days(self.planting_date, int(growth_days))		
		
    def _validate_plot_availability(self):		
        """Block submit if plot is already Planted by another active record"""		
        if self.farm_plot:		
            plot_status = frappe.db.get_value("Farm Plot", self.farm_plot, "plot_status")		
            if plot_status == "Planted" and self.is_new():		
                frappe.throw(		
                    _("Farm Plot {0} is already <b>Planted</b>. "		
                      "Please choose an available plot.").format(self.farm_plot)		
                )		
		
    def _validate_area(self):		
        """Warn if area_planted exceeds plot area"""		
        if self.farm_plot and self.area_planted:		
            plot_area = frappe.db.get_value("Farm Plot", self.farm_plot, "area")		
            if plot_area and self.area_planted > plot_area:		
                frappe.msgprint(		
                    _("Area planted ({0} Ha) exceeds plot area ({1} Ha).").format(		
                        self.area_planted, plot_area		
                    ),		
                    alert=True,		
                    indicator="orange"		
                )		
		
    # ── On Submit ────────────────────────────────────────────		
    def on_submit(self):		
        self._update_farm_plot("Planted")		
		
    def _update_farm_plot(self, status):		
        """Update Farm Plot status, current_crop, and current_planting"""		
        if not self.farm_plot:		
            return		
        plot = frappe.get_doc("Farm Plot", self.farm_plot)		
        plot.plot_status = status		
        if status == "Planted":		
            plot.current_crop = self.crop		
            plot.current_planting = self.name		
        else:		
            plot.current_crop = None		
            plot.current_planting = None		
        plot.save(ignore_permissions=True)		
        frappe.msgprint(		
            _("Farm Plot <b>{0}</b> updated to <b>{1}</b>.").format(		
                self.farm_plot, status		
            ),		
            alert=True, indicator="green"		
        )		
		
    # ── On Cancel ────────────────────────────────────────────		
    def on_cancel(self):		
        self._update_farm_plot("Available")		

