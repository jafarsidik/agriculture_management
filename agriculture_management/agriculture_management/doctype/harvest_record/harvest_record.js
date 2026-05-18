// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Harvest Line", {		
		
    gross_weight(frm, cdt, cdn) { _recalc_line(frm, cdt, cdn); },		
    tare_weight(frm, cdt, cdn)  { _recalc_line(frm, cdt, cdn); },		
    market_price(frm, cdt, cdn) { _recalc_line(frm, cdt, cdn); },		
    harvest_lines_remove(frm)   { _recalc_harvest_totals(frm); }		
});		
		
function _recalc_line(frm, cdt, cdn) {		
    let row = locals[cdt][cdn];		
    let net = (row.gross_weight || 0) - (row.tare_weight || 0);		
    frappe.model.set_value(cdt, cdn, "net_weight", net);		
    frappe.model.set_value(cdt, cdn, "total_value", net * (row.market_price || 0));		
    _recalc_harvest_totals(frm);		
}		
		
function _recalc_harvest_totals(frm) {		
    let gross = 0, net = 0, val = 0;		
    (frm.doc.harvest_lines || []).forEach(r => {		
        gross += (r.gross_weight || 0);		
        net   += (r.net_weight  || 0);		
        val   += (r.total_value || 0);		
    });		
    frm.set_value("total_gross_weight", gross);		
    frm.set_value("total_net_weight",   net);		
    frm.set_value("total_value",        val);		
		
    // Recalc yield variance		
    let est = frm.doc.estimated_yield || 0;		
    if (est > 0) {		
        frm.set_value("yield_variance", (((net - est) / est) * 100).toFixed(2));		
    }		
}		
		
// Auto-fill from Planting Record		
frappe.ui.form.on("Harvest Record", {		
    planting_record(frm) {		
        if (!frm.doc.planting_record) return;		
        frappe.db.get_value(		
            "Planting Record",		
            frm.doc.planting_record,		
            ["farm", "farm_plot", "crop", "season", "estimated_yield", "yield_unit"],		
            (r) => {		
                if (!r) return;		
                frm.set_value("farm",            r.farm);		
                frm.set_value("farm_plot",       r.farm_plot);		
                frm.set_value("crop",            r.crop);		
                frm.set_value("season",          r.season);		
                frm.set_value("estimated_yield", r.estimated_yield);		
                frm.set_value("yield_unit",      r.yield_unit);		
            }		
        );		
    }		
});		

