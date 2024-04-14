// Copyright (c) 2023, jan and contributors
// For license information, please see license.txt

frappe.ui.form.on('Gcash Transactions', {
    refresh: function () {
        if(cur_frm.doc.docstatus && !cur_frm.doc.capital){
             if(cur_frm.doc.status === 'UNPAID'){
              cur_frm.add_custom_button("Paid", () => {
                  cur_frm.call({
                      doc:cur_frm.doc,
                      method: "paid",
                      async: false,
                      callback: function () {
                          cur_frm.reload_doc()
                      }
                  })
              }).css("background-color", "green").css("color", "white").css("font-weight", "bold")
              cur_frm.add_custom_button("Sent Back", () => {
                  cur_frm.call({
                      doc:cur_frm.doc,
                      method: "sent_back_to_gcash",
                      async: false,
                      callback: function () {
                          cur_frm.reload_doc()
                      }
                  })
              }).css("background-color", "orange").css("color", "white").css("font-weight", "bold")
        } else if (cur_frm.doc.status === 'UNCLAIMED'){
            cur_frm.add_custom_button("Claimed", () => {
                  cur_frm.call({
                      doc:cur_frm.doc,
                      method: "claimed",
                        args: {},
                      async: false,
                      callback: function () {
                          cur_frm.reload_doc()
                      }
                  })
              }).css("background-color", "#00BBB2").css("font-weight", "bold")
        } else if (cur_frm.doc.status === 'SETTLED'){
            cur_frm.add_custom_button("UNPAID", () => {
                  cur_frm.call({
                      doc:cur_frm.doc,
                      method: "change_status",
                        args: {
                          status: "UNPAID"
                        },
                      async: false,
                      callback: function () {
                          cur_frm.reload_doc()
                      }
                  })
              }).css("background-color", "#FF7A7A").css("font-weight", "bold")
              cur_frm.add_custom_button("UNCLAIM", () => {
                  cur_frm.call({
                      doc:cur_frm.doc,
                      method: "change_status",
                        args: {
                          status: "UNCLAIMED"
                        },
                      async: false,
                      callback: function () {
                          cur_frm.reload_doc()
                      }
                  })
              }).css("background-color", "blue").css("font-weight", "bold").css("color", "white")
        }
        }

    },
    partial_payment: function () {
      cur_frm.doc.balance = cur_frm.doc.amount - cur_frm.doc.partial_payment
        cur_frm.refresh_field("balance")
    },
//     amount: function () {
//         if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//
//     },
// 	profit_is_in_gcash: function () {
//         if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//
//     },
//     status: function () {
//         if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//
//     },
//     cash_or_gcash: function () {
//         if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//
//     },
//     deduct_fee_from_amount:function () {
//        if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//     },
//     method: function () {
//        if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//     },
// profit: function () {
//        if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//     },
//     no_charge: function () {
//          if(cur_frm.doc.amount){
//              cur_frm.call({
//                 doc: cur_frm.doc,
//                 method: "compute_amounts",
//                 async: false
//             })
//         }
//     },
    // onload_post_render: function () {
    //     if(cur_frm.is_new()){
	 //         cur_frm.call({
    //             doc: cur_frm.doc,
    //             method: "get_balances",
    //             async: false,
    //              callback: function (r) {
    //                  cur_frm.set_df_property("capital", "hidden", r.message)
    //              }
    //         })
    //     }
    //
    // }
});
