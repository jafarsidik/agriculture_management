// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Farm Sales Line", {		
    harvest_record(frm, cdt, cdn) {		
        let row = locals[cdt][cdn];		
        if (!row.harvest_record) return;		
        frappe.db.get_value("Harvest Record", row.harvest_record, ["crop","yield_unit"], (r) => {		
            if (r) {		
                frappe.model.set_value(cdt, cdn, "crop", r.crop);		
                frappe.model.set_value(cdt, cdn, "unit", r.yield_unit || "Kg");		
            }		
        });		
    },		
    quantity(frm, cdt, cdn)    { _recalc_sales_line(frm, cdt, cdn); },		
    unit_price(frm, cdt, cdn)  { _recalc_sales_line(frm, cdt, cdn); },		
    sales_lines_remove(frm)    { _recalc_sales_total(frm); }		
});		
		
function _recalc_sales_line(frm, cdt, cdn) {		
    let row = locals[cdt][cdn];		
    frappe.model.set_value(cdt, cdn, "total",		
        (row.quantity || 0) * (row.unit_price || 0));		
    _recalc_sales_total(frm);		
}		
		
function _recalc_sales_total(frm) {		
    let sub = (frm.doc.sales_lines || []).reduce((s, r) => s + (r.total || 0), 0);		
    frm.set_value("subtotal", sub);		
    frm.set_value("grand_total",		
        sub - (frm.doc.discount || 0) + (frm.doc.tax || 0));		
}		
		
frappe.ui.form.on("Farm Sales Order", {		
    discount(frm) { _recalc_sales_total(frm); },		
    tax(frm)      { _recalc_sales_total(frm); }		
});		
		

