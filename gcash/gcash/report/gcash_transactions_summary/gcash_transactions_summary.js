// Copyright (c) 2023, jan and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Gcash Transactions Summary"] = {
	"filters": [
		{
			"fieldname":"summary",
			"label": __("Summary"),
			"fieldtype": "Check",
		},
		{
			"fieldname":"for_tomorrow",
			"label": __("For Tomorrow"),
			"fieldtype": "Check",
		},
		{
			"fieldname":"profit_summary",
			"label": __("Profit Summary"),
			"fieldtype": "Check",
		},
		{
			"fieldname":"customer",
			"label": __("Customer"),
			"fieldtype": "Data",
		},
		{
			"fieldname":"from_date",
			"label": __("From Date"),
			"fieldtype": "Date",
		},
		{
			"fieldname":"to_date",
			"label": __("To Date"),
			"fieldtype": "Date",
		}

	],
	"formatter": function(value, row, column, data, default_formatter) {
		value = default_formatter(value, row, column, data);
		console.log(column)
		 if (column.id === "total_all_amount") {
            value = "<span style='color:red!important;font-weight:bold;font-size: 20px'>" + value + "</span>";
		}


		return value;
	},
};

