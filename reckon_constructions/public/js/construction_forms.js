frappe.ui.form.on("Project", {
    refresh(frm) {
        if (!frm.doc.construction_status) return;
        frm.add_custom_button(__("Open Project Dashboard"), () => {
            frappe.route_options = { project: frm.doc.name };
            frappe.set_route("project-dashboard");
        });
    },
});

frappe.ui.form.on("Rate Analysis", {
    refresh(frm) {
        frm.set_intro(
            __("Rate Analysis builds the explainable cost per unit for a BOQ line. It combines the assembly, materials, labour, equipment, overhead, and markup into the rate used by the BOQ.")
        );
    },
});

frappe.ui.form.on("Construction BOQ", {
    onload(frm) {
        if (frm.__opened_in_workbench) return;
        frm.__opened_in_workbench = true;
        frappe.route_options = frm.is_new() ? {} : { boq: frm.doc.name };
        frappe.set_route("boq-workbench");
    },
    refresh(frm) {
        frm.set_intro(
            __("This is the saved BOQ record used by approvals, revisions, measurements, progress certificates, quotations, and invoices. Use BOQ Workbench for faster engineer-friendly entry.")
        );
    },
});
