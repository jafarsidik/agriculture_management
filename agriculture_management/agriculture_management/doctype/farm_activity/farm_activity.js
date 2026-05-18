// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Activity Worker", {
    worker(frm, cdt, cdn) {		
        // Auto-fill wage_rate from Farm Worker		
        let row = locals[cdt][cdn];		
        if (!row.worker) return;		
        frappe.db.get_value("Farm Worker", row.worker, ["hourly_rate", "daily_wage_rate"], (r) => {		
            if (r) {		
                frappe.model.set_value(cdt, cdn, "wage_rate", r.hourly_rate || 0);		
            }		
        });		
    },		
		
    hours_worked(frm, cdt, cdn) { _recalc_worker_wage(frm, cdt, cdn); },		
    wage_rate(frm, cdt, cdn)    { _recalc_worker_wage(frm, cdt, cdn); },		
    overtime_hours(frm, cdt, cdn) { _recalc_worker_wage(frm, cdt, cdn); },		
    overtime_rate(frm, cdt, cdn)  { _recalc_worker_wage(frm, cdt, cdn); },		
		
    workers_remove(frm) { _recalc_totals(frm); }		
});		
		
function _recalc_worker_wage(frm, cdt, cdn) {		
    let row = locals[cdt][cdn];		
    let base     = (row.hours_worked || 0) * (row.wage_rate || 0);		
    let overtime = (row.overtime_hours || 0) * (row.overtime_rate || row.wage_rate || 0);		
    frappe.model.set_value(cdt, cdn, "total_wage", base + overtime);	
    _recalc_totals(frm);		
}		
		
// ── Child: Activity Input ────────────────────────────────────		
frappe.ui.form.on("Activity Input", {		
		
    input_item(frm, cdt, cdn) {		
        // Auto-fill rate and unit from Farm Input		
        let row = locals[cdt][cdn];		
        if (!row.input_item) return;		
        frappe.db.get_value("Farm Input", row.input_item, ["unit_price", "default_uom"], (r) => {		
            if (r) {		
                frappe.model.set_value(cdt, cdn, "rate", r.unit_price || 0);		
                frappe.model.set_value(cdt, cdn, "unit", r.default_uom || "");		
            }		
        });		
    },		
		
    quantity(frm, cdt, cdn) { _recalc_input_amount(frm, cdt, cdn); },		
    rate(frm, cdt, cdn)     { _recalc_input_amount(frm, cdt, cdn); },		
    inputs_used_remove(frm) { _recalc_totals(frm); }		
});		
		
function _recalc_input_amount(frm, cdt, cdn) {		
    let row = locals[cdt][cdn];		
    frappe.model.set_value(cdt, cdn, "total_amount",		
        (row.quantity || 0) * (row.rate || 0));		
    _recalc_totals(frm);		
}		
		
// ── Child: Activity Equipment ────────────────────────────────		
frappe.ui.form.on("Activity Equipment", {		
		
    usage_hours(frm, cdt, cdn) { _recalc_equip_cost(frm, cdt, cdn); },		
    fuel_used(frm, cdt, cdn)   { _recalc_equip_cost(frm, cdt, cdn); },		
    equipment_used_remove(frm) { _recalc_totals(frm); }		
});		
		
function _recalc_equip_cost(frm, cdt, cdn) {		
    let row = locals[cdt][cdn];		
    // Simple: usage_cost = usage_hours * depreciation per hour (depreciation_yearly / 2000 hrs)		
    if (row.equipment && row.usage_hours) {		
        frappe.db.get_value("Farm Equipment", row.equipment, "depreciation_yearly", (r) => {		
            if (r && r.depreciation_yearly) {		
                let cost_per_hr = r.depreciation_yearly / 2000;		
                frappe.model.set_value(cdt, cdn, "usage_cost",		
                    Math.round((row.usage_hours || 0) * cost_per_hr));		
                _recalc_totals(frm);		
            }		
        });		
    }		
}		
		
// ── Recalculate all totals ───────────────────────────────────		
function _recalc_totals(frm) {		
    let labor_cost = (frm.doc.worker || []).reduce((s, r) => s + (r.total_wage || 0), 0);		
    let input_cost = (frm.doc.inputs_used || []).reduce((s, r) => s + (r.total_amount || 0), 0);		
    let equip_cost = (frm.doc.equipment_used || []).reduce((s, r) => s + (r.usage_cost || 0), 0);		
		
    frm.set_value("total_labor_cost", labor_cost);		
    frm.set_value("total_input_cost", input_cost);		
    frm.set_value("total_equip_cost", equip_cost);		
    frm.set_value("total_cost", labor_cost + input_cost + equip_cost);		
}		
		
// ── Parent: calc duration on time change ─────────────────────		
frappe.ui.form.on("Farm Activity", {		
    start_time(frm) { _calc_duration(frm); },		
    end_time(frm)   { _calc_duration(frm); }		
});		
		
function _calc_duration(frm) {		
    if (!frm.doc.start_time || !frm.doc.end_time) return;		
    let [sh, sm] = frm.doc.start_time.split(":").map(Number);		
    let [eh, em] = frm.doc.end_time.split(":").map(Number);		
    let minutes = (eh * 60 + em) - (sh * 60 + sm);		
    if (minutes > 0) frm.set_value("duration_hours", (minutes / 60).toFixed(2));		
}		

