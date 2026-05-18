// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Labor Attendance", {		
		
    worker(frm) {		
        if (!frm.doc.worker) return;		
        frappe.db.get_value(		
            "Farm Worker", frm.doc.worker,		
            ["hourly_rate", "daily_wage_rate", "assigned_farm"],		
            (r) => {		
                if (!r) return;		
                frm.set_value("wage_rate",      r.hourly_rate || 0);		
                frm.set_value("overtime_rate",  (r.hourly_rate || 0) * 1.5);		
                if (!frm.doc.farm && r.assigned_farm) {		
                    frm.set_value("farm", r.assigned_farm);		
                }		
            }		
        );		
    },		
		
    check_in(frm)  { _calc_attendance_hours(frm); },		
    check_out(frm) { _calc_attendance_hours(frm); },		
		
    wage_rate(frm)       { _calc_total_wage(frm); },		
    hours_worked(frm)    { _calc_total_wage(frm); },		
    overtime_hours(frm)  { _calc_total_wage(frm); },		
    overtime_rate(frm)   { _calc_total_wage(frm); },		
    transport_allowance(frm) { _calc_net_pay(frm); },		
    meal_allowance(frm)      { _calc_net_pay(frm); },		
		
    status(frm) {		
        if (frm.doc.status === "Absent") {		
            frm.set_value("total_wage",  0);		
            frm.set_value("net_pay",     0);		
            frm.set_value("hours_worked", 0);		
        }		
    }		
});		
		
function _calc_attendance_hours(frm) {		
    if (!frm.doc.check_in || !frm.doc.check_out) return;		
    let [sh, sm] = frm.doc.check_in.split(":").map(Number);		
    let [eh, em] = frm.doc.check_out.split(":").map(Number);		
    let minutes  = (eh * 60 + em) - (sh * 60 + sm);		
    if (minutes > 0) {		
        frm.set_value("hours_worked", (minutes / 60).toFixed(2));		
        _calc_total_wage(frm);		
    }		
}		
		
function _calc_total_wage(frm) {		
    if (frm.doc.status === "Absent") return;		
    let base     = (frm.doc.hours_worked   || 0) * (frm.doc.wage_rate     || 0);		
    let overtime = (frm.doc.overtime_hours || 0) * (frm.doc.overtime_rate || 0);		
    frm.set_value("total_wage", base + overtime);		
    _calc_net_pay(frm);		
}		
		
function _calc_net_pay(frm) {		
    frm.set_value("net_pay",		
        (frm.doc.total_wage           || 0)		
        + (frm.doc.transport_allowance || 0)		
        + (frm.doc.meal_allowance      || 0)		
    );		
}		
