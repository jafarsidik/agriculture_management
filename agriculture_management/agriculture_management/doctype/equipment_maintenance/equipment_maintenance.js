// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt
frappe.ui.form.on("Equipment Maintenance", {		
    refresh(frm) {		
        // Add "Mark Complete" custom button for submitted records		
        if (frm.doc.docstatus === 1 && frm.doc.status !== "Completed") {		
            frm.add_custom_button(__("Mark Complete"), () => {		
                frappe.confirm(		
                    __("Mark this maintenance as Completed?"),		
                    () => {		
                        frappe.call({		
                            doc:    frm.doc,		
                            method: "mark_complete",		
                            callback(r) {		
                                frappe.show_alert({ message: r.message, indicator: "green" });		
                                frm.reload_doc();		
                            }		
                        });		
                    }		
                );		
            }, __("Actions"));		
        }		
    },		
		
    // Auto-fill parts total on quantity/unit_price change		
});		
		
frappe.ui.form.on("Maintenance Part", {		
    quantity(frm, cdt, cdn)   { _recalc_part(frm, cdt, cdn); },		
    unit_price(frm, cdt, cdn) { _recalc_part(frm, cdt, cdn); },		
    parts_used_remove(frm)    { _recalc_parts_total(frm); }		
});		
		
function _recalc_part(frm, cdt, cdn) {		
    let row = locals[cdt][cdn];		
    frappe.model.set_value(cdt, cdn, "total",		
        (row.quantity || 0) * (row.unit_price || 0));		
    _recalc_parts_total(frm);		
}		
		
function _recalc_parts_total(frm) {		
    let parts_cost = (frm.doc.parts_used || []).reduce((s, r) => s + (r.total || 0), 0);		
    frm.set_value("parts_cost", parts_cost);		
    frm.set_value("maintenance_cost", (frm.doc.labor_cost || 0) + parts_cost);		
}		
		
frappe.ui.form.on("Equipment Maintenance", {		
    labor_cost(frm) {		
        frm.set_value("maintenance_cost",		
            (frm.doc.labor_cost || 0) + (frm.doc.parts_cost || 0));		
    }		
});		
