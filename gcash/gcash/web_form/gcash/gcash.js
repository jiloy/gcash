frappe.ready(function() {
$('form').on('submit', function(event) {
    setTimeout(() => {
        window.location.reload();
    },1000)
})
    // frappe.web_form.on('status', (field, value) => {
    //     if(value && value === 'CLAIM'){
    //         document.getElementsByClassName("submit-btn")[0].style.display = "none"
    //         document.getElementsByClassName("discard-btn")[0].style.display = "none"
    //         var div = document.getElementsByClassName('form-column')[0];
    //         var button = document.createElement('button');
    //         // button.classList.add('btn');
    //         // button.classList.add('btn-primary');
    //         // button.classList.add('btn-sm');
    //         // button.classList.add('ml-2');
    //         // button.classList.add('custom-btn');
    //         button.textContent = 'Claim';
    //         div.appendChild(button);
    //
    //         button.addEventListener("click", () => {
    //             console.log("BUTTON CLICKED")
    //         })
    //     } else {
    //         document.getElementsByClassName("submit-btn")[0].style.display = ""
    //         document.getElementsByClassName("discard-btn")[0].style.display = ""
    //     document.getElementsByClassName("custom-btn")[0].style.display = "none"
    //
    //     }
    // })
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

    frappe.web_form.on('reference_number', (field, value) => {
        if(value && frappe.web_form.get_value("status") === 'CLAIM'){
            // <button type="submit" class="submit-btn btn btn-primary btn-sm ml-2">Save</button>

            console.log("HEEERE")
            frappe.call({
                method: "gcash.gcash.doctype.gcash_transactions.gcash_transactions.fetch_reference_number",
                args: {
                    reference_number: value
                },
                freeze: true,
                freeze_message: "Fetching Profit...",
                callback: function (r) {
                    if(r.message.length > 0){
                            frappe.web_form.set_value("profit", r.message[0].profit)
                            frappe.web_form.set_value("amount", r.message[0].amount)
                    }
                }
            })
        }
    })

})