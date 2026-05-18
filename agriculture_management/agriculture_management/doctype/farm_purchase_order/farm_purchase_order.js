// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.ui.form.on("PO Lines", {		
    input_item(frm, cdt, cdn) {		
        let row = locals[cdt][cdn];		
        if (!row.input_item) return;		
        frappe.db.get_value("Farm Input", row.input_item, ["unit_price","default_uom"], (r) => {		
            if (r) {		
                frappe.model.set_value(cdt, cdn, "unit_price", r.unit_price || 0);		
                frappe.model.set_value(cdt, cdn, "unit",       r.default_uom || "");		
                _recalc_po_line(frm, cdt, cdn);		
            }		
        });		
    },		
    quantity(frm, cdt, cdn)   { _recalc_po_line(frm, cdt, cdn); },		
    unit_price(frm, cdt, cdn) { _recalc_po_line(frm, cdt, cdn); },		
    po_lines_remove(frm)      { _recalc_po_total(frm); }		
});		
		
function _recalc_po_line(frm, cdt, cdn) {		
    let row = locals[cdt][cdn];		
    frappe.model.set_value(cdt, cdn, "amount",		
        (row.quantity || 0) * (row.unit_price || 0));		
    _recalc_po_total(frm);		
}		
		
function _recalc_po_total(frm) {		
    let sub = (frm.doc.po_lines || []).reduce((s, r) => s + (r.amount || 0), 0);		
    frm.set_value("subtotal",    sub);		
    frm.set_value("grand_total", sub - (frm.doc.discount || 0) + (frm.doc.tax || 0));		
}		
		
frappe.ui.form.on("Farm Purchase Order", {		
    discount(frm) { _recalc_po_total(frm); },		
    tax(frm)      { _recalc_po_total(frm); }		
});		
