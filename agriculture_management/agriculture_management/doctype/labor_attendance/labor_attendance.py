# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class LaborAttendance(Document):

    def validate(self):
        self._auto_fill_wage_rate()
        self._calc_hours_worked()
        self._calc_total_wage()
        self._validate_no_duplicate()

    def _auto_fill_wage_rate(self):
        """Pull hourly_rate from Farm Worker if not manually set"""
        if self.worker and not self.wage_rate:
            rate = frappe.db.get_value("Farm Worker", self.worker, "hourly_rate")
            if rate:
                self.wage_rate = rate

        if self.worker and not self.overtime_rate:
            # Default overtime = 1.5x regular rate
            rate = frappe.db.get_value("Farm Worker", self.worker, "hourly_rate") or 0
            self.overtime_rate = rate * 1.5

    def _calc_hours_worked(self):
        """Calculate hours_worked from check_in / check_out (HH:MM)"""
        if self.check_in and self.check_out:
            try:
                # FIX: replaced map(int, ...) with list comprehension
                sh, sm = [int(x) for x in self.check_in.split(":")]
                eh, em = [int(x) for x in self.check_out.split(":")]
                minutes = (eh * 60 + em) - (sh * 60 + sm)
                if minutes > 0:
                    self.hours_worked = round(minutes / 60, 2)
            except Exception:
                pass
        elif self.status == "Half Day":
            worker_type = frappe.db.get_value("Farm Worker", self.worker, "worker_type")
            self.hours_worked = 4.0   # half-day default

    def _calc_total_wage(self):
        """total_wage = (hours_worked × wage_rate) + (overtime_hours × overtime_rate)"""
        if self.status in ("Absent",):
            self.total_wage = 0
            self.net_pay    = 0
            return

        base     = float(self.hours_worked or 0) * float(self.wage_rate or 0)
        overtime = float(self.overtime_hours or 0) * float(self.overtime_rate or 0)
        self.total_wage = base + overtime
        self.net_pay    = self.total_wage + float(self.transport_allowance or 0) + float(self.meal_allowance or 0)

    def _validate_no_duplicate(self):
        """Prevent duplicate attendance record for same worker + date"""
        existing = frappe.db.get_value(
            "Labor Attendance",
            {
                "worker":          self.worker,
                "attendance_date": self.attendance_date,
                "docstatus":       ["!=", 2],          # not cancelled
                "name":            ["!=", self.name]   # not self
            },
            "name"
        )
        if existing:
            frappe.throw(
                _("Attendance for <b>{0}</b> on <b>{1}</b> already exists: {2}").format(
                    self.worker, self.attendance_date, existing
                )
            )