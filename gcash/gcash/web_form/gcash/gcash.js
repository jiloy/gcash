frappe.ready(function() {

    frappe.web_form.on('amount', (field, value) => {
            console.log("HETEEEER IN AFTER LOAD")

            frappe.call({
                method: "gcash.gcash.doctype.gcash_transactions.gcash_transactions.compute_amount",
                args: {
                    status: frappe.web_form.get_value("status"),
                    amount: frappe.web_form.get_value("amount"),
                    no_charge: frappe.web_form.get_value("no_charge"),
                    edit_profit: frappe.web_form.get_value("edit_profit"),
                    profit: frappe.web_form.get_value("profit") ? frappe.web_form.get_value("profit") : 0,
                },
                freeze: true,
                freeze_message: "Fetching Profit...",
                callback: function (r) {
                    frappe.web_form.set_value("profit", r.message)
                }
            })

        })
     frappe.web_form.on('no_charge', (field, value) => {
            console.log("HETEEEER IN AFTER LOAD")

            frappe.call({
                method: "gcash.gcash.doctype.gcash_transactions.gcash_transactions.compute_amount",
                args: {
                    status: frappe.web_form.get_value("status"),
                    amount: frappe.web_form.get_value("amount"),
                    no_charge: frappe.web_form.get_value("no_charge"),
                    edit_profit: frappe.web_form.get_value("edit_profit"),
                    profit: frappe.web_form.get_value("profit") ? frappe.web_form.get_value("profit") : 0,
                },
                freeze: true,
                freeze_message: "Fetching Profit...",
                callback: function (r) {
                    frappe.web_form.set_value("profit", r.message)
                }
            })

        })


})