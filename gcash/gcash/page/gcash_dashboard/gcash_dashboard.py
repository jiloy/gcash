import frappe



@frappe.whitelist()
def get_data():
    cash_in = [
        {
            "amount": 100,
            "status": "SETTLED",
        },
        {
            "amount": 100,
            "status": "UNPAID",
        }
    ]


    for x in cash_in:
        