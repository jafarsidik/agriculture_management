# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe		
from frappe import _		
from frappe.model.document import Document


class HarvestRecord(Document):
	
	def validate(self):		
		self._auto_fill_from_planting()		
		self._calc_harvest_totals()		
		self._calc_yield_variance()		
		
	def _auto_fill_from_planting(self):		
		"""Pull farm, farm_plot, crop from linked Planting Record"""		
		if not self.planting_record:		
			return		
		pr = frappe.db.get_value(		
			"Planting Record",		
			self.planting_record,		
			["farm", "farm_plot", "crop", "season", "estimated_yield"],		
			as_dict=True		
		)		
		if pr:		
			if not self.farm:        self.farm        = pr.farm		
			if not self.farm_plot:   self.farm_plot   = pr.farm_plot		
			if not self.crop:        self.crop        = pr.crop		
			if not self.season:      self.season      = pr.season		
			if not self.estimated_yield:		
				self.estimated_yield = pr.estimated_yield		
		
	def _calc_harvest_totals(self):		
		"""Sum gross and net weight across all Harvest Line rows"""		
		total_gross = total_net = total_value = 0		
		for line in self.get("harvest_lines") or []:		
			line.tare_weight = line.tare_weight or 0		
			line.net_weight  = (line.gross_weight or 0) - line.tare_weight		
			line.total_value = line.net_weight * (line.market_price or 0)		
			total_gross += (line.gross_weight or 0)		
			total_net   += line.net_weight		
			total_value += line.total_value		
		
		self.total_gross_weight = total_gross		
		self.total_net_weight   = total_net		
		self.total_value        = total_value		
		
	def _calc_yield_variance(self):		
		"""yield_variance % = (actual - estimated) / estimated * 100"""		
		if self.estimated_yield and self.estimated_yield != 0:		
			self.yield_variance = round(		
				((self.total_net_weight - self.estimated_yield) / self.estimated_yield) * 100, 2		
			)		
		else:		
			self.yield_variance = 0		
		
	# ── On Submit ────────────────────────────────────────────		
	def on_submit(self):		
		self._update_planting_record()		
		self._update_farm_plot()		
		
	def _update_planting_record(self):		
		"""Mark Planting Record as Harvested and fill actual_harvest date"""		
		if not self.planting_record:		
			return		
		frappe.db.set_value("Planting Record", self.planting_record, {		
			"status":         "Harvested",		
			"actual_harvest": self.harvest_date		
		})		
		
	def _update_farm_plot(self):		
		"""Set Farm Plot back to Available and clear current crop"""		
		if not self.farm_plot:		
			return		
		frappe.db.set_value("Farm Plot", self.farm_plot, {		
			"plot_status":      "Available",		
			"current_crop":     None,		
			"current_planting": None,		
			"last_harvest_date": self.harvest_date		
		})		
		frappe.msgprint(		
			_("Farm Plot <b>{0}</b> is now <b>Available</b>.").format(self.farm_plot),		
			alert=True, indicator="green"		
		)		
		
	# ── On Cancel ────────────────────────────────────────────		
	def on_cancel(self):		
		"""Revert Planting Record and Farm Plot on cancel"""		
		if self.planting_record:		
			frappe.db.set_value("Planting Record", self.planting_record, {		
				"status": "Active", "actual_harvest": None		
			})		
		if self.farm_plot:		
			frappe.db.set_value("Farm Plot", self.farm_plot, {		
				"plot_status":      "Planted",		
				"current_crop":     self.crop,		
				"current_planting": self.planting_record		
			})		
		

