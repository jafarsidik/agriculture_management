# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe		
from frappe import _		
from frappe.model.document import Document		



class InputStockRecord(Document):
	
	def validate(self):		
		self.total_value = (self.quantity or 0) * (self.unit_price or 0)		
		
	def on_submit(self):		
		self._update_balance(sign=1)		
		
	def on_cancel(self):		
		self._update_balance(sign=-1)		
		
	def _update_balance(self, sign):		
		"""		
		sign = +1  → apply transaction normally		
		sign = -1  → reverse (on cancel)		
		"""		
		is_in = "In" in (self.transaction_type or "")		
		delta  = (self.quantity or 0) * sign * (1 if is_in else -1)		
		
		balance_name = frappe.db.get_value(		
			"Input Stock Balance",		
			{"farm": self.farm, "input_item": self.input_item},		
			"name"		
		)		
		
		if balance_name:		
			bal = frappe.get_doc("Input Stock Balance", balance_name)		
			new_stock = (bal.current_stock or 0) + delta		
		else:		
			# Create new balance record on first "In" transaction		
			if not is_in:		
				frappe.throw(		
					_("No stock balance found for {0} at {1}. "		
					  "Record a purchase first.").format(self.input_item, self.farm)		
				)		
			bal = frappe.new_doc("Input Stock Balance")		
			bal.farm       = self.farm		
			bal.input_item = self.input_item		
			bal.unit       = self.unit		
			new_stock      = delta		
		
		if new_stock < 0:		
			frappe.throw(		
				_("Stock for <b>{0}</b> cannot go below zero. "		
				  "Current: {1}, Deducting: {2}").format(		
					self.input_item,		
					(bal.current_stock or 0),		
					abs(delta)		
				)		
			)		
		
		bal.current_stock    = new_stock		
		bal.last_updated     = frappe.utils.now()		
		bal.last_transaction = self.name		
		
		# Auto-set stock status		
		min_stock = frappe.db.get_value("Farm Input", self.input_item, "min_stock") or 0		
		if new_stock <= 0:		
			bal.stock_status = "Out of Stock"		
		elif min_stock and new_stock <= min_stock:		
			bal.stock_status = "Low"		
		else:		
			bal.stock_status = "Normal"		
		
		bal.save(ignore_permissions=True)		
		self.balance_after = new_stock		

