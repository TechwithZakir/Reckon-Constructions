frappe.listview_settings["Construction BOQ"] = {
    primary_action() {
        open_boq_workbench();
    },
    onload(listview) {
        frappe.set_route("boq-register");
    },
};

function open_boq_workbench(boq) {
    frappe.route_options = boq ? { boq } : {};
    frappe.set_route("boq-workbench");
}
