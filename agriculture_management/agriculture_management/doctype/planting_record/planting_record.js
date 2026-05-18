// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Planting Record", {

    // ── Auto-fill expected_harvest when planting_date or crop changes ──		
    planting_date(frm) {		
        frm.trigger("calc_expected_harvest");		
    },		
		
    crop(frm) {		
        frm.trigger("calc_expected_harvest");		
    },		
		
    calc_expected_harvest(frm) {		
        if (!frm.doc.planting_date || !frm.doc.crop) return;		
		
        frappe.db.get_value("Crop", frm.doc.crop, "growth_duration", (r) => {		
            if (r && r.growth_duration) {		
                let d = frappe.datetime.add_days(frm.doc.planting_date, r.growth_duration);		
                frm.set_value("expected_harvest", d);		
            }		
        });		
    },		
		
    // ── Auto-fill area_planted from farm_plot ──		
    farm_plot(frm) {		
        if (!frm.doc.farm_plot) return;		
        frappe.db.get_value("Farm Plot", frm.doc.farm_plot, "area", (r) => {		
            if (r && r.area) {		
                frm.set_value("area_planted", r.area);		
            }		
        });		
    },		
		
    // ── Auto-fill seed_cost when seed_source or seed_qty changes ──		
    seed_source(frm) { 
        frm.trigger("calc_seed_cost");
    
    },		
    seed_qty(frm) {
        
        frm.trigger("calc_seed_cost");
        
    },		
		
    calc_seed_cost(frm) {		
        if (!frm.doc.seed_source || !frm.doc.seed_qty) return;		
       
        frappe.db.get_value("Farm Input", frm.doc.seed_source, "unit_price", (r) => {	
            if (r && r.unit_price) {		
                frm.set_value("seed_cost", frm.doc.seed_qty * r.unit_price);		
            }		
        });		
    },		
		
    // ── Auto-fill estimated_yield from crop ──		
    refresh(frm) {		
        if (frm.doc.area_planted && frm.doc.crop) {		
            frm.trigger("calc_estimated_yield");		
        }		
    },		
		
    area_planted(frm) { frm.trigger("calc_estimated_yield"); },		
		
    calc_estimated_yield(frm) {		
        if (!frm.doc.crop || !frm.doc.area_planted) return;		
        frappe.db.get_value("Crop", frm.doc.crop, "expected_yield", (r) => {		
            if (r && r.expected_yield) {		
                frm.set_value("estimated_yield", r.expected_yield * frm.doc.area_planted);		
            }		
        });		
    }		

});
