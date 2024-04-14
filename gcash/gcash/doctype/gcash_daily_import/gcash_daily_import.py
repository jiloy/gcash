# Copyright (c) 2023, jan and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class GcashDailyImport(Document):
	@frappe.whitelist()
	def set_posting_date(self):
		self.posting_date = self.get_posting_date(self.details.split("\n"))
		f_details = [x for x in self.details.split("\n") if x]

		self.number_of_transactions = len(f_details) - 1
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
			if x:
				t_split = x.split("-")
				if t_split[0].lower().replace(" ","") == "return":
					self.return_transaction(t_split[1],t_split[3],t_split[2],x)
				if t_split[0].lower().replace(" ","") == "borrow":
					self.borrow_transaction(t_split[1],t_split[-1],t_split[2],x)

				if t_split[0].lower().replace(" ","") == "cashin" or t_split[0].lower().replace(" ","") == "load":
					self.cashin_transaction(t_split,x)
				if t_split[0].lower().replace(" ","") == "banktransfer":
					self.banktransfer_transaction(t_split,x)

				if t_split[0].lower().replace(" ","") == "cashout":
					self.cashout_transaction(t_split,x)

				if t_split[0].lower().replace(" ","") == "unclaimed":
					self.unclaimed_transaction(t_split,x)

				if t_split[0].lower().replace(" ","") == "paid":
					self.paid_transaction(t_split,x)

				if t_split[0].lower().replace(" ","") == "claimed":
					self.claimed_transaction(t_split,x)
				if t_split[0].lower().replace(" ","") == "profit":
					self.profit_transaction(t_split,x)
				if t_split[0].lower().replace(" ","") == "withdraw":
					self.withdraw_transaction(t_split,x)
				if t_split[0].lower().replace(" ","") == "deposit":
					self.deposit_transaction(t_split,x)

	def paid_transaction(self,t_split,x):
		# paid - name - amount - profit
		# paid - name - amount - profit - sent back
		gt = frappe.db.sql(""" SELECT * FROM `tabGcash Transactions` WHERE remarks like %s and amount=%s and status='UNPAID' and docstatus=1 ORDER BY creation DESC""",("%" + t_split[1] + "%",t_split[2].replace(",","")),as_dict=1)
		if len(gt) > 0:
			gtr = frappe.get_doc("Gcash Transactions",gt[0].name)
			if len(t_split) >= 4 and t_split[-1].lower() == "no charge":
				gtr.remarks += x
				gtr.save()
				gtr.paid()

			elif len(t_split) >= 4 and t_split[-1].lower() == "sent back":
				if t_split[3] != 'sent back':
					gtr.additional_profit = abs(float(t_split[3].replace(",","")) - gtr.profit)
				gtr.remarks += x
				gtr.save()
				gtr.sent_back_to_gcash()

			else:
				if len(t_split) >= 4 and t_split[3] != 'sent back':
					gtr.additional_profit = abs(float(t_split[3].replace(",","")) - gtr.profit)
				gtr.remarks += x
				gtr.save()
				gtr.paid()
	def cashin_transaction(self, t_split,x):
		status = "SETTLED" if len(t_split) == 2 or (len(t_split) > 2 and t_split[2].lower() != "unpaid") else "UNPAID"
		obj = {
			"doctype": "Gcash Transactions",
			"date": self.posting_date,
			"status": status,
			"method": "Cash In",
			"amount": float(t_split[1].replace(",","")),
			"remarks": t_split[3] if status == "UNPAID" else x,
			"no_per_day": status == "UNPAID" and t_split[3].lower() in ['novy',"mama",'ante lizel','ante liezl',"cle rezty","lola",'eric','mam jill','maam jill',''],
			"edit_profit": len(t_split) > 2 and t_split[2].lower() != "unpaid",
			"no_charge": len(t_split) > 2 and t_split[2].lower() == "no charge"
		}
		if len(t_split) > 2 and t_split[2].lower() not in ["unpaid","no charge"]:
			obj['profit'] = float(t_split[-1])

		if len(t_split) > 2 and t_split[2].lower() == "no charge":
			obj['profit'] = 0
		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()
	def banktransfer_transaction(self, t_split,x):
		obj = {
			"doctype": "Gcash Transactions",
			"date": self.posting_date,
			"status": "SETTLED",
			"method": "Cash In",
			"amount": float(t_split[1].replace(",","")),
			"remarks":  x,
			"gcash_to_bank": 1
		}
		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()

	def cashout_transaction(self, t_split,x):
		# Cashout-amount-reference-time released
		# Cashout-amount-profit-reference-time released
		# Cashout-amount-profit-less charge/no charge/profit in gcash-reference-time released
		# Cashout-amount-less charge/no charge/profit in gcash-reference-time released
		status = "SETTLED"
		obj = {
			"doctype": "Gcash Transactions",
			"date": self.posting_date,
			"status": status,
			"method": "Cash Out",
			"amount": float(t_split[1].replace(",","")),
			"deduct_fee_from_amount": len(t_split) > 4 and t_split[-3].lower() == 'less charge',
			"no_charge": len(t_split) > 4 and t_split[-3].lower() == 'no charge',
			"profit_is_in_gcash": len(t_split) > 4 and t_split[-3].lower() == "profit in gcash",
			"edit_profit": len(t_split) > 4 and t_split[2].lower() not in ['less charge','no charge','profit in gcash'] and len(str(t_split[2])) < 5,
			"remarks": x,
			"reference_number": t_split[-1]
		}
		if len(t_split) > 4 and t_split[2].lower() not in ['less charge', 'no charge', 'profit in gcash'] and len(str(t_split[2])) < 5:
			obj['profit'] = float(t_split[2])
		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()
	def unclaimed_transaction(self, t_split,x):
		check_ref = frappe.db.sql(""" SELECT * FROM `tabGcash Transactions` WHERE reference_number=%s""",t_split[2],as_dict=1)
		if len(check_ref) == 0:
			status = "UNCLAIMED"
			obj = {
				"doctype": "Gcash Transactions",
				"date": self.posting_date,
				"status": status,
				"method": "Cash Out",
				"amount": float(t_split[1].replace(",","")),
				"remarks": x,
				"reference_number": t_split[2]
			}
			gt = frappe.get_doc(obj).insert()
			gt.submit()
			frappe.db.commit()

	def claimed_transaction(self, t_split,x):
		#Claimed-Reference Number-time received
		#Claimed-Reference Number-time received-less charge/no charge/profit in gcash
		print(t_split[2].replace(",",""))
		gt = frappe.db.sql(
			""" SELECT * FROM `tabGcash Transactions` WHERE reference_number=%s and status='UNCLAIMED' and docstatus=1 ORDER BY creation DESC""",
			(t_split[2].replace(",","")), as_dict=1)
		print(gt)
		if len(gt) > 0:
			gtr = frappe.get_doc("Gcash Transactions", gt[0].name)
			if t_split[-1] == 'less charge':
				gtr.deduct_fee_from_amount = 1
				gtr.time_received = t_split[3]
				if len(t_split) > 4 and t_split[4] not in ['less charge', 'no charge', 'profit in gcash'] and ":" not in t_split[4]:
					gtr.edit_profit = 1
					gtr.additional_profit = abs(gtr.profit - float(t_split[4]))
				gtr.save()
				frappe.db.commit()
			elif t_split[-1] == 'no charge':
				gtr.no_charge = 1
				gtr.profit = 0
				gtr.time_received = t_split[3]
				if len(t_split) > 4 and  t_split[4] not in ['less charge', 'no charge', 'profit in gcash'] and ":" not in t_split[4]:
					gtr.edit_profit = 1
					gtr.additional_profit = abs(gtr.profit - float(t_split[4]))
				gtr.save()
				frappe.db.commit()
			elif t_split[-1] == 'profit in gcash':
				gtr.profit_in_gcash = 1
				gtr.time_received = t_split[3]
				if len(t_split) > 4 and  t_split[4] not in ['less charge', 'no charge', 'profit in gcash'] and ":" not in t_split[4]:
					gtr.edit_profit = 1
					gtr.additional_profit = abs(gtr.profit - float(t_split[4]))
				gtr.save()
				frappe.db.commit()
			else:
				if len(t_split) > 4 and  t_split[4] not in ['less charge', 'no charge', 'profit in gcash'] and ":" not in t_split[4]:
					gtr.edit_profit = 1
					gtr.additional_profit = abs(gtr.profit - float(t_split[4]))
				gtr.time_received = t_split[3]


			gtr1 = frappe.get_doc("Gcash Transactions", gt[0].name)

			gtr1.claimed()

	def return_transaction(self,lender,amount,cash_or_gcash,remarks):
		obj = {
			"doctype": "Gcash Transactions",
			"status": "RETURN",
			"date": self.posting_date,
			"cash_or_gcash": cash_or_gcash.capitalize(),
			"lender": lender.capitalize(),
			"amount":float(amount.replace(",","")),
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
			"cash_or_gcash": cash_or_gcash.capitalize(),
			"lender": lender.capitalize(),
			"amount":float(amount.replace(",","")),
			"remarks": remarks
		}
		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()
	def withdraw_transaction(self,t_split,x):
		obj = {
			"doctype": "Gcash Transactions",
			"status": "WITHDRAW",
			"date": self.posting_date,
			"amount":float(t_split[-1].replace(",","")),
			"remarks": x
		}
		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()
	def deposit_transaction(self,t_split,x):
		obj = {
			"doctype": "Gcash Transactions",
			"status": "DEPOSIT",
			"date": self.posting_date,
			"amount":float(t_split[-1].replace(",","")),
			"remarks": x
		}
		gt = frappe.get_doc(obj).insert()
		gt.submit()
		frappe.db.commit()

	def profit_transaction(self,t_split,x):
		if len(t_split) > 3:
			obj = {
				"doctype": "Gcash Transactions",
				"status": "PROFIT EXPENSE",
				"cash_or_gcash": t_split[2].capitalize(),
				"date": self.posting_date,
				"amount":float(t_split[1].replace(",","")),
				"remarks": x
			}
			gt = frappe.get_doc(obj).insert()
			gt.submit()
			frappe.db.commit()
		else:
			obj =  {
				"doctype": "Gcash Transactions",
				"status": "PROFIT",
				"cash_or_gcash": t_split[2].capitalize(),
				"date": self.posting_date,
				"amount":float(t_split[1].replace(",","")),
				"remarks": x
			}
			gt = frappe.get_doc(obj).insert()
			gt.submit()
			frappe.db.commit()
