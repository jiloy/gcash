# Copyright (c) 2023, jan and contributors
# For license information, please see license.txt

import frappe, math
from frappe.model.document import Document

class GcashImport(Document):
	def get_posting_date(self,details):
		months = {
			"January": "01",
			"February": "02",
			"March": "03",
			"April": "04",
			"May": "05",
			"June": "06",
			"July": "07",
			"August": "08",
			"September": "09",
			"October": "10",
			"November": "11",
			"December": "12",
		}
		t_split = details[0].split(" ")
		month = months[t_split[1]]
		day = t_split[-1]
		if len(str(day)) == 1:
			day = "0" + day
		return str(frappe.utils.now_datetime().date().year) + "-"+ month + "-"+ day
	@frappe.whitelist()
	def import_transactions(self):
		self.posting_date = self.get_posting_date(self.details.split("\n"))
		for x in self.details.split("\n"):
			t_split = x.split("-")
			if t_split[0].lower().replace(" ","") == "return":
				self.return_transaction(t_split[1],t_split[-1],t_split[2],x)
			if t_split[0].lower().replace(" ","") == "borrow":
				self.borrow_transaction(t_split[1],t_split[-1],t_split[2],x)

	def create_transaction(self, type,t_split,status):
		amount = t_split[-1]
		obj = {
			"doctype": "Gcash Transactions",
			"status": status,
			"amount": amount,
			"profit": math.ceil(self.amount * 0.01)  if self.amount >= 500 and not self.no_charge and not self.edit_profit else 5 if not self.no_charge and not self.edit_profit else self.profit if self.edit_profit else 0

		}

	def return_transaction(self,lender,amount,cash_or_gcash,remarks):
		obj = {
			"doctype": "Gcash Transactions",
			"status": "RETURN",
			"date": self.posting_date,
			"cash_or_gcash": cash_or_gcash,
			"lender": lender,
			"amount":float(amount),
			"remarks": remarks
		}
		print(obj)

		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()

	def borrow_transaction(self,lender,amount,cash_or_gcash,remarks):
		obj = {
			"doctype": "Gcash Transactions",
			"status": "BORROW",
			"date": self.posting_date,
			"cash_or_gcash": cash_or_gcash,
			"lender": lender,
			"amount":float(amount),
			"remarks": remarks
		}
		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()