// Copyright (c) 2023, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gcash Daily Import', {
	details: function(frm) {
if(cur_frm.doc.details){
    cur_frm.call({
        doc: cur_frm.doc,
        method: "set_posting_date",
        callback: function () {
            
        }
    })
}
	}
});
