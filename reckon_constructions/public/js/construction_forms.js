frappe.ui.form.on("Rate Analysis", {
    refresh(frm) {
        frm.set_intro(
            __("Rate Analysis builds the explainable cost per unit for a BOQ line. It combines the assembly, materials, labour, equipment, overhead, and markup into the rate used by the BOQ.")
        );
    },
});

frappe.ui.form.on("Construction BOQ", {
    refresh(frm) {
        frm.set_intro(
            __("This is the saved BOQ record used by approvals, revisions, measurements, progress certificates, quotations, and invoices. Use BOQ Workbench for faster engineer-friendly entry.")
        );

        if (!frm.is_new()) {
            frm.add_custom_button(__("Open in BOQ Workbench"), () => {
                frappe.route_options = { boq: frm.doc.name };
                frappe.set_route("boq-workbench");
            });
        }
    },
});
