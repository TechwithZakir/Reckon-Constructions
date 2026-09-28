frappe.listview_settings["Construction BOQ"] = {
    onload(listview) {
        listview.page.add_inner_button(__("Open BOQ Workbench"), () => {
            frappe.set_route("boq-workbench");
        });
    },
};
