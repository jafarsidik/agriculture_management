# Copyright (c) 2026, Jafar Sidik and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document

class FarmCostSheet(Document):

    def validate(self):
        self._calc_all()

    # ── Public helper: call from "Refresh Data" button ───────
    @frappe.whitelist()
    def refresh_data(self):
        self._fetch_labor_cost()
        self._fetch_input_cost()
        self._fetch_equipment_cost()
        self._fetch_overhead_cost()
        self._fetch_revenue()
        self._fetch_yield()
        self._calc_all()
        self.save()
        return _("Cost sheet data refreshed successfully.")

    # ── Fetch from source documents ──────────────────────────
    def _fetch_labor_cost(self):
        """SUM Labor Attendance total_wage filtered by farm + season"""
        if self.farm_plot:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(la.total_wage), 0)
                FROM `tabLabor Attendance` la
                JOIN `tabFarm Activity` fa ON la.activity = fa.name
                WHERE fa.farm_plot = %(plot)s
                  AND la.farm = %(farm)s
                  AND la.docstatus = 1
            """, {"plot": self.farm_plot, "farm": self.farm})
            self.labor_cost = result[0][0] if result else 0
        else:
            # FIX: Replaced f-string with fully parameterized query using CASE/COALESCE
            # to avoid SQL injection (line 52).
            # The season date range filter is applied only when self.season is set,
            # using a dummy always-true condition otherwise.
            if self.season:
                season = frappe.db.get_value(
                    "Crop Season", self.season, ["start_date", "end_date"], as_dict=True
                )
                result = frappe.db.sql("""
                    SELECT IFNULL(SUM(total_wage), 0)
                    FROM `tabLabor Attendance`
                    WHERE farm = %(farm)s
                      AND docstatus = 1
                      AND attendance_date BETWEEN %(start_date)s AND %(end_date)s
                """, {
                    "farm": self.farm,
                    "start_date": season.start_date if season else "1900-01-01",
                    "end_date":   season.end_date   if season else "9999-12-31",
                })
            else:
                result = frappe.db.sql("""
                    SELECT IFNULL(SUM(total_wage), 0)
                    FROM `tabLabor Attendance`
                    WHERE farm = %(farm)s
                      AND docstatus = 1
                """, {"farm": self.farm})

            self.labor_cost = result[0][0] if result else 0

    def _fetch_input_cost(self):
        """SUM Activity Input total_amount via Farm Activity"""
        base_filter = {"docstatus": 1, "farm": self.farm}
        if self.farm_plot:
            base_filter["farm_plot"] = self.farm_plot

        activities = frappe.get_all(
            "Farm Activity", filters=base_filter, pluck="name"
        )
        if not activities:
            self.input_cost = 0
            return

        result = frappe.db.sql("""
            SELECT IFNULL(SUM(ai.total_amount), 0)
            FROM `tabActivity Input` ai
            WHERE ai.parent IN %(activities)s
        """, {"activities": activities})
        self.input_cost = result[0][0] if result else 0

    def _fetch_equipment_cost(self):
        """SUM Activity Equipment usage_cost + fuel_cost + Equipment Maintenance cost"""
        base_filter = {"docstatus": 1, "farm": self.farm}
        if self.farm_plot:
            base_filter["farm_plot"] = self.farm_plot

        activities = frappe.get_all(
            "Farm Activity", filters=base_filter, pluck="name"
        )
        usage_cost = 0
        if activities:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(ae.usage_cost), 0) + IFNULL(SUM(ae.fuel_cost), 0)
                FROM `tabActivity Equipment` ae
                WHERE ae.parent IN %(activities)s
            """, {"activities": activities})
            usage_cost = result[0][0] if result else 0

        maint_cost = 0
        if activities:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(em.maintenance_cost), 0)
                FROM `tabEquipment Maintenance` em
                WHERE em.farm_activity IN %(activities)s
                  AND em.docstatus = 1
            """, {"activities": activities})
            maint_cost = result[0][0] if result else 0

        self.equipment_cost   = usage_cost
        self.maintenance_cost = maint_cost

    def _fetch_overhead_cost(self):
        """SUM Farm Expense grand_total for this farm + season"""
        # FIX: Replaced f-string with two explicit parameterized queries (line 119).
        if self.season:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(grand_total), 0)
                FROM `tabFarm Expense`
                WHERE farm = %(farm)s
                  AND docstatus = 1
                  AND season = %(season)s
            """, {"farm": self.farm, "season": self.season})
        else:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(grand_total), 0)
                FROM `tabFarm Expense`
                WHERE farm = %(farm)s
                  AND docstatus = 1
            """, {"farm": self.farm})

        self.overhead_cost = result[0][0] if result else 0

    def _fetch_revenue(self):
        """SUM Farm Sales Order grand_total for this farm + season"""
        # FIX: Replaced f-string with two explicit parameterized queries (line 135).
        if self.season:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(grand_total), 0)
                FROM `tabFarm Sales Order`
                WHERE farm = %(farm)s
                  AND docstatus = 1
                  AND status != 'Cancelled'
                  AND season = %(season)s
            """, {"farm": self.farm, "season": self.season})
        else:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(grand_total), 0)
                FROM `tabFarm Sales Order`
                WHERE farm = %(farm)s
                  AND docstatus = 1
                  AND status != 'Cancelled'
            """, {"farm": self.farm})

        self.total_revenue = result[0][0] if result else 0

    def _fetch_yield(self):
        """SUM Harvest Record total_net_weight for this farm + plot + crop"""
        # FIX: Replaced f-string with explicit parameterized query branches (line 155).
        # Each combination of optional filters gets its own safe query.
        values = {"farm": self.farm}

        if self.farm_plot and self.crop:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(total_net_weight), 0)
                FROM `tabHarvest Record`
                WHERE farm = %(farm)s
                  AND docstatus = 1
                  AND farm_plot = %(farm_plot)s
                  AND crop = %(crop)s
            """, {**values, "farm_plot": self.farm_plot, "crop": self.crop})

        elif self.farm_plot:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(total_net_weight), 0)
                FROM `tabHarvest Record`
                WHERE farm = %(farm)s
                  AND docstatus = 1
                  AND farm_plot = %(farm_plot)s
            """, {**values, "farm_plot": self.farm_plot})

        elif self.crop:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(total_net_weight), 0)
                FROM `tabHarvest Record`
                WHERE farm = %(farm)s
                  AND docstatus = 1
                  AND crop = %(crop)s
            """, {**values, "crop": self.crop})

        else:
            result = frappe.db.sql("""
                SELECT IFNULL(SUM(total_net_weight), 0)
                FROM `tabHarvest Record`
                WHERE farm = %(farm)s
                  AND docstatus = 1
            """, values)

        self.total_yield = result[0][0] if result else 0

    # ── Calculate derived KPIs ───────────────────────────────
    def _calc_all(self):
        self.total_cost = (
            (self.labor_cost         or 0)
            + (self.input_cost       or 0)
            + (self.equipment_cost   or 0)
            + (self.maintenance_cost or 0)
            + (self.overhead_cost    or 0)
        )

        area = self.total_area or 1
        self.cost_per_ha = round(self.total_cost / area, 2) if area else 0

        yield_kg = self.total_yield or 0
        self.cost_per_kg = round(self.total_cost / yield_kg, 4) if yield_kg else 0

        self.gross_profit  = (self.total_revenue or 0) - self.total_cost
        revenue            = self.total_revenue or 1
        self.profit_margin = round((self.gross_profit / revenue) * 100, 2) if revenue else 0
        self.roi           = round((self.gross_profit / self.total_cost) * 100, 2) if self.total_cost else 0