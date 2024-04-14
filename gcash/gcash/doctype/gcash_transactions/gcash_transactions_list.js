frappe.listview_settings['Gcash Transactions'] = {
	add_fields: ["status"],
	get_indicator: function (doc) {

		if (["SETTLED"].includes(doc.status)) {
			return [__(doc.status), "green", "status,=," + doc.status];
		} else if (["UNPAID"].includes(doc.status)) {
			return [__(doc.status), "red", "status,=," + doc.status];
		} else if (["UNCLAIMED"].includes(doc.status)) {
			return [__(doc.status), "blue", "status,=," + doc.status];
		}else if (["BORROW"].includes(doc.status)) {
			return [__(doc.status), "black", "status,=," + doc.status];
		}else if (["RETURN"].includes(doc.status)) {
			return [__(doc.status), "pink", "status,=," + doc.status];
		}else if (["WITHDRAW","DEPOSIT"].includes(doc.status)) {
			return [__(doc.status), "yellow", "status,=," + doc.status];
		} else if (["PROFIT EXPENSE", "Profit"].includes(doc.status)) {
			return [__(doc.status), "brown", "status,=," + doc.status];
		}

	},
};