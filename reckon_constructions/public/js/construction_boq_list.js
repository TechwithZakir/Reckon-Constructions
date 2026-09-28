frappe.listview_settings["Construction BOQ"] = {
    onload(listview) {
        listview.page.set_primary_action(__("New Construction BOQ"), () => open_boq_workbench());

        const result = listview.page.wrapper && listview.page.wrapper[0];
        if (result) {
            result.addEventListener("click", function (event) {
                const row = event.target.closest(".list-row-container, .list-row");
                const name = row && row.dataset.name;
                if (!name || event.target.closest("button, input, select, .list-row-checkbox")) return;
                event.preventDefault();
                event.stopPropagation();
                open_boq_workbench(name);
            }, true);
        }
    },
};

function open_boq_workbench(boq) {
    frappe.route_options = boq ? { boq } : {};
    frappe.set_route("boq-workbench");
}
