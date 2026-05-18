// Copyright (c) 2026, Jafar Sidik and contributors
// For license information, please see license.txt

frappe.ui.form.on("Farm Cost Sheet", {		
    refresh(frm) {		
        // "Refresh Data" button to pull aggregated costs from source docs		
        if (frm.doc.docstatus === 0) {		
            frm.add_custom_button(__("Refresh Data"), () => {		
                frappe.call({		
                    doc:    frm.doc,		
                    method: "refresh_data",		
                    freeze: true,		
                    freeze_message: __("Calculating costs..."),		
                    callback(r) {		
                        frappe.show_alert({ message: r.message, indicator: "green" });		
                        frm.reload_doc();		
                    }		
                });		
            }, __("Tools"));		
        }		
    }		
});		
		
