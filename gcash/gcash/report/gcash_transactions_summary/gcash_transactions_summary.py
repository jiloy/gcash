# Copyright (c) 2023, jan and contributors
# For license information, please see license.txt

import frappe

def get_columns():
	return [
		{"fieldname": "date","fieldtype": "Date","label": "Date",},
		{"fieldname": "time","fieldtype": "Time","label": "Time","width": 80},
		{"fieldname": "status","fieldtype": "Data","label": "Status","width": 120},
		{"fieldname": "method","fieldtype": "Data","label": "Method","width": 120},
		{"fieldname": "amount","fieldtype": "Currency","label": "Amount","width": 120},
		{"fieldname": "profit","fieldtype": "Currency","label": "Profit","width": 120},
		{"fieldname": "gcash_money_after_transaction","fieldtype": "Currency","label": "Gcash Money After Transaction","width": 220},
		{"fieldname": "cash_on_hand_after_transaction","fieldtype": "Currency","label": "Cash on Hand After Transaction","width": 250},
		{"fieldname": "remarks","fieldtype": "Data","label": "Remarks","width": 300}
	]
def get_summary_columns():
	return [
		{"fieldname": "remarks", "fieldtype": "Data", "label": "Customer","width": 200 },
		{"fieldname": "total_amount", "fieldtype": "Data", "label": "Total Amount","width": 200 },
		{"fieldname": "total_profit", "fieldtype": "Data", "label": "Total Profit","width": 200 },
		{"fieldname": "total_additional_profit", "fieldtype": "Data", "label": "Total Additional Profit","width": 200 },
		{"fieldname": "total_all_amount", "fieldtype": "Data", "label": "Amount Due","width": 150},
	]
def get_summary_columns_per_customer():
	return [
		# {"fieldname": "date", "fieldtype": "Date", "label": "Date","width": 150 },
		{"fieldname": "amount", "fieldtype": "Data", "label": "Amount","width": 150 },
		{"fieldname": "profit", "fieldtype": "Data", "label": "Charge","width": 150 },
		{"fieldname": "days_unpaid", "fieldtype": "Data", "label": "Days Unpaid","width": 150 },
		{"fieldname": "total_additional_charge", "fieldtype": "Data", "label": "Total Additional Charge","width": 200 },
		{"fieldname": "total_all_amount", "fieldtype": "Data", "label": "Amount Due","width": 150},
	]
def get_profit_summary_columns_per_customer():
	return [
		{"fieldname": "date", "fieldtype": "Data", "label": "Date","width": 200 },
		{"fieldname": "amount", "fieldtype": "Data", "label": "Amount","width": 150 },
	]
def execute(filters=None):
	columns, data = get_columns() if not filters.get("summary") and not filters.get("profit_summary") else get_summary_columns() if not filters.get("customer") and not filters.get("profit_summary") else get_summary_columns_per_customer() if filters.get("summary") and not filters.get("profit_summary") else get_profit_summary_columns_per_customer(), []
	conditions = ""
	if filters.get("from_date") and filters.get("to_date"):
		conditions += " and date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"), filters.get("to_date"))
	total_profit = 0
	number_of_days = 0
	if not filters.get("summary") and not filters.get("profit_summary"):
		if not filters.get("customer"):
			data = frappe.db.sql(""" SELECT	* FROM `tabGcash Transactions` WHERE docstatus=1 ORDER BY creation DESC""",as_dict=1)
		else:
			data = frappe.db.sql(
				""" SELECT	* FROM `tabGcash Transactions` WHERE docstatus=1 and remarks like %s ORDER BY creation DESC""","%" + filters.get("customer") + "%", as_dict=1)

	elif filters.get("profit_summary") and not filters.get("summary"):
		profit_filter = " GL.posting_date >= '2024-01-01'"

		if filters.get("from_date") and filters.get("to_date"):
			profit_filter = "  GL.posting_date BETWEEN '{0}' and '{1}' ".format(filters.get("from_date"), filters.get("to_date"))
		data = frappe.db.sql(""" SELECT (SUM(GL.debit) - SUM(GL.credit)) as amount, GL.posting_date as date FROM `tabGL Entry` GL 
							INNER JOIN `tabJournal Entry` JE ON JE.name = GL.voucher_no
 							WHERE GL.account='Gcash Profit - C' and GL.is_cancelled=0 and {0} and
 							JE.is_consolidate=0
 							GROUP BY GL.posting_date 
 							ORDER BY GL.posting_date DESC""".format(profit_filter),as_dict=1)
		# datas = frappe.db.sql(""" SELECT * FROM `tabGcash Transactions` WHERE docstatus=1 and status in ('SETTLED', 'PROFIT','PROFIT EXPENSE') {0} and date >= '2024-01-01' ORDER BY date DESC""".format(conditions),as_dict=1)

		# data = []
		current_date = ""
		amount = 0
        #
		# for x in datas:
		# 	if not current_date:
		# 		current_date = x.date
		# 		amount += x.profit + x.additional_profit
		# 		if x.status == 'PROFIT':
		# 			amount += x.amount
		# 		elif x.status == 'PROFIT EXPENSE':
		# 			amount -= x.amount
		# 	elif current_date and current_date == x.date:
		# 		amount += x.profit + x.additional_profit
		# 		if x.status == 'PROFIT':
		# 			amount += x.amount
		# 		elif x.status == 'PROFIT EXPENSE':
		# 			amount -= x.amount
		# 	elif current_date and current_date != x.date:
		# 		data.append({
		# 			"date": current_date,
		# 			"amount": round(amount,2)
		# 		})
		# 		number_of_days += 1
		# 		total_profit += round(amount, 2)
		# 		current_date = x.date
		# 		amount = x.profit + x.additional_profit
		# 		if x.status == 'PROFIT':
		# 			amount += x.amount
		# 		elif x.status == 'PROFIT EXPENSE':
		# 			amount -= x.amount
		# data.append({
		# 	"date": str(current_date),
		# 	"amount": round(amount,2)
		# })
		# number_of_days += 1
		# total_profit += round(amount,2)
	else:
		if not filters.get("customer"):
			data = frappe.db.sql(""" SELECT 
											SUM(amount) as total_amount, 
											SUM(profit) as total_profit, 
											SUM(additional_profit) as total_additional_profit, 
											SUM(amount + profit + additional_profit) as total_all_amount, 
											remarks
										FROm `tabGcash Transactions`
										WHERE status='UNPAID' and docstatus=1 GROUP BY remarks ORDER BY total_amount DESC""",as_dict=1)
		else:
			data = frappe.db.sql(""" SELECT 
											amount, 
											profit, 
											additional_profit, 
											amount + profit + additional_profit as total_all_amount,
											date,time
										FROm `tabGcash Transactions`
										WHERE status='UNPAID' and docstatus=1 and remarks like %s ORDER BY creation DESC""",("%" + filters.get("customer") + "%"),
								 as_dict=1)
			total = 0
			for x in data:

				date_time = frappe.utils.get_datetime(str(x.date))
				days = (frappe.utils.now_datetime() - date_time).days
				x['days_unpaid'] = str(days)
				x['total_additional_charge'] = x.additional_profit
				if filters.get("for_tomorrow"):
					x.total_all_amount += x.profit
				total += x.total_all_amount
			data.append({
				"total_additional_charge": "TOTAL",
				"total_all_amount":total
			})
	if total_profit > 0:
		data.append({
			"date": "Total",
			"amount": total_profit
		})
		data.append({
			"date": "Average Profit per Day",
			"amount": round(total_profit / number_of_days,2)
		})
	return columns, data


