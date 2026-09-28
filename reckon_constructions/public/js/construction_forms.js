function flatten_project_tabs(frm) {
    const layout = frm.layout;
    if (!layout?.tabs?.length) return;

    layout.tab_link_container?.closest(".form-tabs-list").hide();
    layout.tabs_content?.removeClass("tab-content");

    layout.tabs.forEach((tab) => {
        tab.tab_link?.closest("li").hide();
        tab.wrapper
            ?.removeClass("tab-pane fade active show hide")
            .css({ display: "block", opacity: 1 });
    });
}

function hide_retired_project_fields(frm) {
    if (frm.fields_dict.construction_sales_order) {
        frm.toggle_display("construction_sales_order", false);
    }
}

frappe.ui.form.on("Project", {
    refresh(frm) {
        hide_retired_project_fields(frm);
        flatten_project_tabs(frm);
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

function load_measurement_boq_context(frm) {
    if (!frm.doc.boq) return;

    const request_key = `${frm.doc.boq}|${frm.doc.boq_line_key || ""}`;
    if (frm.__measurement_context_request === request_key) return;
    frm.__measurement_context_request = request_key;

    frappe.call({
        method: "reckon_constructions.constructions.doctype.measurement_sheet.measurement_sheet.get_boq_line_context",
        args: { boq: frm.doc.boq, line_key: frm.doc.boq_line_key || "" },
    }).then((response) => {
        const context = response.message || {};
        const lines = context.lines || [];
        frm.set_df_property("boq_line_key", "options", ["", ...lines.map((line) => line.line_key)].join("\n"));

        if (context.project && frm.doc.project !== context.project) {
            frm.set_value("project", context.project);
        }

        const selected = context.selected;
        if (!selected) return;
        frm.set_value({
            output_uom: selected.uom || frm.doc.output_uom,
            boq_item_description: selected.description || "",
            boq_item_quantity: selected.quantity || 0,
        });
        frm.set_intro(
            __("Measuring {0} | BOQ quantity: {1} {2}", [
                selected.description || selected.line_key,
                selected.quantity || 0,
                selected.uom || "",
            ])
        );
    });
}

frappe.ui.form.on("Measurement Sheet", {
    setup(frm) {
        frm.set_query("boq", () => ({
            filters: frm.doc.project ? { project: frm.doc.project } : {},
        }));
    },
    onload(frm) {
        load_measurement_boq_context(frm);
    },
    boq(frm) {
        frm.__measurement_context_request = null;
        load_measurement_boq_context(frm);
    },
    boq_line_key(frm) {
        frm.__measurement_context_request = null;
        load_measurement_boq_context(frm);
    },
    refresh(frm) {
        load_measurement_boq_context(frm);
        if (frm.doc.boq) {
            frm.add_custom_button(__("Open BOQ Workbench"), () => {
                frappe.route_options = { boq: frm.doc.boq };
                frappe.set_route("boq-workbench");
            }, __("BOQ"));
        }
    },
});
