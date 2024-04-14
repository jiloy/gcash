import frappe


def create_lender_party_type():
    party_type = frappe.db.sql(""" SELECT * FROM `tabParty Type` WHERE name='Lender' """)
    if len(party_type) == 0:
        obj = {
            "doctype": "Party Type",
            "party_type": "Lender",
            "account_type": "Payable"
        }
        frappe.get_doc(obj).insert(ignore_permissions=1)
        frappe.db.commit()


def update_unpaid_transactions():
    gcash = frappe.db.sql(""" SELECT * FROM `tabGcash Transactions` WHERE status='UNPAID'""",as_dict=1)

    for x in gcash:
        if x.date and x.time and not x.no_per_day:
            # date_time = frappe.utils.get_datetime(str(x.date) + " " + str(x.time))
            # days = (frappe.utils.now_datetime() - date_time).days
            days = frappe.utils.date_diff(frappe.utils.now_datetime().date(),x.date)
            frappe.db.sql(""" UPDATE `tabGcash Transactions` SET additional_profit=%s WHERE name=%s""",(int(days) * x.profit, x.name))
            frappe.db.commit()



def check_sent_back_to_gcash():
    transactions = frappe.db.sql(""" SELECT GT.name, GJE.journal_entry, GT.additional_profit FROM `tabGcash Transactions` GT INNER JOIN `tabGcash Journal Entries` GJE
                                    ON GJE.parent = GT.name WHERE GT.docstatus=1 and GJE.remarks='SENT BACK TO GCASH' and GT.profit=0 and GT.creation < '2023-10-17' ORDER BY GJE.parent ASC""",as_dict=1)
    total = 0
    for x in transactions:
        print("==============+TRANSACTIONS================")
        print(x.name)
        print(x.journal_entry)
        total += x.additional_profit

    print(total)