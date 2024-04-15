# Copyright (c) 2023, jan and contributors
# For license information, please see license.txt

import frappe, math
from frappe.model.document import Document

class GcashTransactions(Document):
	def on_cancel(self):
		for x in self.journal_entries:
			jv = frappe.get_doc("Journal Entry",x.journal_entry)
			if jv.docstatus == 1:
				jv.cancel()
				frappe.db.commit()
	@frappe.whitelist()
	def on_submit_doc(self):
		gcash_account  = "Gcash Wallet - C"
		cash_account  = "Gcash Cash - C"
		profit_account  = "Gcash Profit - C"
		temporary_account  = "Temporary Opening - C"
		borrow_account  = "Gcash Borrow - C"
		accounts = []
		if self.status == 'SETTLED':
			accounts =  [
				{
					"account": cash_account if self.method == 'Cash In' else gcash_account,
					"debit": self.amount if self.method == 'Cash Out' and not self.profit_is_in_gcash else
								self.amount + self.profit if self.method == 'Cash Out' and self.profit_is_in_gcash else self.amount,
					"debit_in_account_currency": self.amount if self.method == 'Cash Out' and not self.profit_is_in_gcash else
								self.amount + self.profit if self.method == 'Cash Out' and self.profit_is_in_gcash else self.amount,
				},
				{
					"account": gcash_account if self.method == 'Cash In' else cash_account,
					"credit": self.amount if self.method == 'Cash Out' and not self.deduct_fee_from_amount else self.amount - self.profit if self.method == 'Cash Out' and self.deduct_fee_from_amount else self.amount,
					"credit_in_account_currency": self.amount if self.method == 'Cash Out' and not self.deduct_fee_from_amount else self.amount - self.profit if self.method == 'Cash Out' and self.deduct_fee_from_amount else self.amount,
				}
			]
			if not self.profit_is_in_gcash and not self.deduct_fee_from_amount and self.profit > 0:
				accounts.append({
					"account": cash_account,
					"debit": self.profit,
					"debit_in_account_currency": self.profit,
				})
			if self.gcash_to_bank:
				accounts += [
					{
						"account": cash_account,
						"debit": 15,
						"debit_in_account_currency": 15
					},
					{
						"account": gcash_account,
						"credit": 15,
						"credit_in_account_currency":15,
					}
				]
			if self.profit > 0:
				accounts += [
					{
						"account": profit_account,
						"debit": self.profit,
						"debit_in_account_currency": self.profit
					},
					{
						"account": temporary_account,
						"credit": self.profit * 2,
						"credit_in_account_currency": self.profit * 2,
					}
				]
		elif self.status == 'UNPAID':
			accounts = [
				{
					"account": gcash_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount,
				},
				{
					"account": temporary_account,
					"debit": self.amount,
					"debit_in_account_currency": self.amount,
				}
			]
		elif self.status == 'BORROW':
			accounts = [
				{
					"account": borrow_account,
					"debit": self.amount,
					"debit_in_account_currency": self.amount,
					"party_type": "Lender",
					"party": self.lender,
				},
				{
					"account": cash_account if self.cash_or_gcash == 'Cash' else gcash_account,
					"debit": self.amount,
					"debit_in_account_currency": self.amount
				},
				{
					"account": temporary_account,
					"credit": self.amount * 2,
					"credit_in_account_currency": self.amount * 2,
				}
			]
		elif self.status == 'RETURN':
			accounts = [
				{
					"account": cash_account if self.cash_or_gcash == 'Cash' else gcash_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount,
				},
				{
					"account": borrow_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount,
					"party_type": "Lender",
					"party": self.lender,
				},
				{
					"account": temporary_account,
					"debit": self.amount * 2,
					"debit_in_account_currency": self.amount * 2,
				}
			]
		elif self.status == 'UNCLAIMED':
			accounts = [
				{
					"account": gcash_account,
					"debit": self.amount,
					"debit_in_account_currency": self.amount,
				},
				{
					"account": temporary_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount,
				}
			]
		elif self.status == 'WITHDRAW':
			accounts = [
				{
					"account": cash_account ,
					"debit": self.amount ,
					"debit_in_account_currency": self.amount,
				},
				{
					"account": gcash_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount,
				}
			]
		elif self.status == 'PROFIT EXPENSE':
			accounts = [
				{
					"account": profit_account,
					"credit": self.amount ,
					"credit_in_account_currency": self.amount,
				},
				{
					"account": cash_account if self.cash_or_gcash == 'Cash' else gcash_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount,
				},
				{
					"account": temporary_account,
					"debit": self.amount,
					"debit_in_account_currency": self.amount * 2,
				}
			]
		elif self.status == 'PROFIT':
			accounts = [
				{
					"account": profit_account,
					"debit": self.amount,
					"debit_in_account_currency": self.amount,
				},
				{
					"account": cash_account if self.cash_or_gcash == 'Cash' else gcash_account,
					"credit": self.amount,
					"debit_in_account_currency": self.amount,
				},
				{
					"account": temporary_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount * 2,
				}
			]
		elif self.status == 'DEPOSIT':
			accounts = [
				{
					"account": gcash_account,
					"debit": self.amount,
					"debit_in_account_currency": self.amount,
				},
				{
					"account": cash_account,
					"credit": self.amount,
					"credit_in_account_currency": self.amount,
				}
			]
		if len(accounts) > 0:
			obj = {
				"doctype": "Journal Entry",
				"voucher_type": "Journal Entry",
				"posting_date": self.date,
				"accounts": accounts,
				"user_remark": self.remarks

			}
			jv = frappe.get_doc(obj).insert()
			jv.submit()
			obj = {
				"doctype": "Gcash Journal Entries",

				"journal_entry": jv.name,
				"remarks": self.status,
				"parent": self.name,
				"parenttype": "Gcash Transactions",
				"parentfield": "journal_entries",
			}
			frappe.get_doc(obj).insert(ignore_permissions=1)
			frappe.db.commit()
	@frappe.whitelist()
	def paid(self):
		cash_account = "Gcash Cash - C"
		profit_account = "Gcash Profit - C"
		temporary_account = "Temporary Opening - C"
		accounts = [
			{
				"account": cash_account,
				"debit": self.amount + self.profit + self.additional_profit,
				"debit_in_account_currency": self.amount + self.profit + self.additional_profit,
			},
			{
				"account": temporary_account,
				"credit": self.amount + self.profit + self.additional_profit,
				"credit_in_account_currency": self.amount + self.profit + self.additional_profit,
			}
		]
		if self.profit > 0:
			accounts += [
				{
					"account": profit_account,
					"debit": self.profit + self.additional_profit,
					"debit_in_account_currency": self.profit + self.additional_profit
				},
				{
					"account": temporary_account,
					"credit": self.profit + self.additional_profit,
					"credit_in_account_currency": self.profit + self.additional_profit,
				}
			]


		print(accounts)
		obj = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": frappe.utils.now_datetime().date(),
			"accounts": accounts,
		}
		jv = frappe.get_doc(obj).insert()
		jv.submit()
		# self.append("journal_entries", {
		# 	"journal_entry": jv.name,
		# 	"remarks": "PAID"
		# })
		obj = {
			"doctype": "Gcash Journal Entries",
			"journal_entry": jv.name,
			"remarks": "PAID",
			"parent": self.name,
			"parenttype": "Gcash Transactions",
			"parentfield": "journal_entries",
		}
		frappe.get_doc(obj).insert()
		frappe.db.commit()
		self.change_status("SETTLED")
	@frappe.whitelist()
	def sent_back_to_gcash(self):
		gcash_account = "Gcash Wallet - C"
		profit_account = "Gcash Profit - C"
		temporary_account = "Temporary Opening - C"
		accounts = [
			{
				"account": gcash_account,
				"debit": (self.amount + self.profit + self.additional_profit) - self.partial_payment,
				"debit_in_account_currency": (self.amount + self.profit + self.additional_profit) - self.partial_payment,
			},
			{
				"account": temporary_account,
				"credit": (self.amount + self.profit + self.additional_profit) - self.partial_payment,
				"credit_in_account_currency": (self.amount + self.profit + self.additional_profit) - self.partial_payment,
			}
		]
		if self.profit > 0 or self.additional_profit > 0:
			accounts += [
				{
					"account": profit_account,
					"debit": self.profit + self.additional_profit,
					"debit_in_account_currency": self.profit + self.additional_profit
				},
				{
					"account": temporary_account,
					"credit": self.profit + self.additional_profit,
					"credit_in_account_currency": self.profit + self.additional_profit,
				}
			]
		print(accounts)
		obj = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": frappe.utils.now_datetime().date(),
			"accounts": accounts,
		}
		jv = frappe.get_doc(obj).insert()
		jv.submit()
		# self.append("journal_entries", {
		# 	"journal_entry": jv.name,
		# 	"remarks": "SENT BACK TO GCASH"
		# })
		# jv.save()
		obj = {
			"doctype": "Gcash Journal Entries",
			"journal_entry": jv.name,
			"remarks": "SENT BACK TO GCASH",
			"parent": self.name,
			"parenttype": "Gcash Transactions",
			"parentfield": "journal_entries",
		}
		frappe.get_doc(obj).insert()
		frappe.db.commit()
		self.change_status("SETTLED")

	@frappe.whitelist()
	def claimed(self):
		cash_account = "Gcash Cash - C"
		profit_account = "Gcash Profit - C"
		temporary_account = "Temporary Opening - C"
		accounts = [
			{
				"account": cash_account,
				"credit": self.amount if not self.deduct_fee_from_amount and not self.profit_is_in_gcash else self.amount - self.profit,
				"credit_in_account_currency": self.amount if not self.deduct_fee_from_amount and not self.profit_is_in_gcash else self.amount - self.profit,
			},
			{
				"account": temporary_account,
				"debit": self.amount if not self.deduct_fee_from_amount and not self.profit_is_in_gcash else self.amount - self.profit,
				"debit_in_account_currency": self.amount if not self.deduct_fee_from_amount and not self.profit_is_in_gcash else self.amount - self.profit,
			}
		]

		if not self.deduct_fee_from_amount and not self.profit_is_in_gcash and self.profit > 0:
			accounts += [
				{
					"account": cash_account,
					"debit": self.profit,
					"debit_in_account_currency": self.profit,
				}
			]
		if self.profit > 0:
			accounts += [
				{
					"account": profit_account,
					"debit": self.profit,
					"debit_in_account_currency": self.profit
				},
				{
					"account": temporary_account,
					"credit": self.profit * 2 if not self.deduct_fee_from_amount and not self.profit_is_in_gcash else self.profit ,
					"credit_in_account_currency": self.profit * 2 if not self.deduct_fee_from_amount and not self.profit_is_in_gcash else self.profit,
				}
			]

		print(accounts)
		obj = {
			"doctype": "Journal Entry",
			"voucher_type": "Journal Entry",
			"posting_date": frappe.utils.now_datetime().date(),
			"accounts": accounts,
		}
		jv = frappe.get_doc(obj).insert()
		jv.submit()
		# self.append("journal_entries", {
		# 	"journal_entry": jv.name,
		# 	"remarks": "CLAIMED"
		# })
		obj = {
			"doctype": "Gcash Journal Entries",
			"journal_entry": jv.name,
			"remarks": "CLAIMED",
			"parent": self.name,
			"parenttype": "Gcash Transactions",
			"parentfield": "journal_entries",
		}
		frappe.get_doc(obj).insert()
		frappe.db.commit()
		self.change_status("SETTLED")
	@frappe.whitelist()
	def change_status(self,status):
		frappe.db.sql(""" UPDATE `tabGcash Transactions` SET status=%s WHERE name=%s """, (status,self.name))
		frappe.db.commit()
	@frappe.whitelist()
	def get_balances(self):
		gcash_transactions = frappe.db.sql(""" SELECT * FROm `tabGcash Transactions` where docstatus=1 ORDER BY creation DESC LIMIT 1""",as_dict=1)

		if len(gcash_transactions) > 0:
			self.gcash_money_before_transaction = gcash_transactions[0].gcash_money_after_transaction
			self.cash_on_hand_before_transaction = gcash_transactions[0].cash_on_hand_after_transaction
			return True
		else:
			self.gcash_money_before_transaction = 0
			self.cash_on_hand_before_transaction = 0
			return False
	def validate(self):
		self.compute_amounts()

		self.on_submit_doc()
		self.docstatus = 1
	@frappe.whitelist()
	def compute_amounts(self):
		if self.status not in ['BORROW','RETURN', 'PROFIT EXPENSE']:
			self.profit = math.ceil(self.amount * 0.01)  if self.amount >= 500 and not self.no_charge and not self.edit_profit else 5 if not self.no_charge and not self.edit_profit else self.profit if self.edit_profit else 0

			# if self.method == 'Cash In':
			# 	self.gcash_money_after_transaction = self.gcash_money_before_transaction - self.amount
			# 	self.cash_on_hand_after_transaction = self.cash_on_hand_before_transaction + self.amount + self.profit
			# elif self.method == "Cash Out":
			# 	self.gcash_money_after_transaction = self.gcash_money_before_transaction + self.amount if not self.profit_is_in_gcash else (self.gcash_money_before_transaction + self.amount + self.profit)
			# 	self.cash_on_hand_after_transaction = (self.cash_on_hand_before_transaction - self.amount) + self.profit if not self.deduct_fee_from_amount and not self.profit_is_in_gcash else (self.cash_on_hand_before_transaction - self.amount) if self.profit_is_in_gcash and not self.deduct_fee_from_amount else (self.cash_on_hand_before_transaction - (self.amount - self.profit)) if self.deduct_fee_from_amount else self.cash_on_hand_before_transaction
		# elif self.status == 'BORROW':
		# 	if self.cash_or_gcash == 'Gcash':
		# 		self.gcash_money_after_transaction = self.gcash_money_before_transaction + self.amount
		# 		self.cash_on_hand_after_transaction = self.cash_on_hand_before_transaction
        #
		# 	else:
		# 		self.gcash_money_after_transaction = self.gcash_money_before_transaction
		# 		self.cash_on_hand_after_transaction = self.cash_on_hand_before_transaction + self.amount
		# elif self.status == 'RETURN':
		# 	if self.cash_or_gcash == 'Gcash':
		# 		self.gcash_money_after_transaction = self.gcash_money_before_transaction - self.amount
		# 		self.cash_on_hand_after_transaction = self.cash_on_hand_before_transaction
        #
		# 	else:
		# 		self.gcash_money_after_transaction = self.gcash_money_before_transaction
		# 		self.cash_on_hand_after_transaction = self.cash_on_hand_before_transaction - self.amount

@frappe.whitelist(allow_guest=1)
def compute_amount(status,amount,no_charge,edit_profit,profit):
	print("HERE")
	if status not in ['BORROW', 'RETURN', 'PROFIT EXPENSE']:
		no_charge = (no_charge != '0')
		edit_profit = (edit_profit != '0')
		profit = math.ceil(float(amount) * 0.01) if float(amount) >= 500 and not no_charge and not edit_profit else 5 if not no_charge and not edit_profit else profit if edit_profit else 0
		print(profit)
		return profit
