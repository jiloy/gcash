frappe.pages['gcash-dashboard'].on_page_load = function(wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: 'Gcash Dashboard',
		single_column: true
	});


}
function fetch_data(page, form_values) {
	frappe.call({
		method: "gcash.gcash.page.gcash_dashboard.gcash_dashboard.get_data",
		args: {},
		freeze: true,
		freeze_message: "Fetching IOU and Loans List...",
		async: false,
		callback: function(resp) {
			if(page.main[0].children.length > 1){
				page.main[0].replaceChild(document.createTextNode(""),page.main[0].children[1])
				page.main.append(frappe.render_template("employee_iou_&_loans", { 'doc':  resp.message}))

			} else {
				page.main.append(frappe.render_template("employee_iou_&_loans", { 'doc':  resp.message}))

			}
		}
	});
}
