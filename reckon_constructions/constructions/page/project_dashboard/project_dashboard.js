frappe.pages["project-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Project Dashboard"),
        single_column: true,
    });

    const project = frappe.route_options && frappe.route_options.construction_project;
    if (!project) {
        $(page.body).html(`<div class="text-muted">${__("Open this page from a Construction Project.")}</div>`);
        return;
    }

    $(page.body).html(`<div class="construction-dashboard text-muted">${__("Loading dashboard...")}</div>`);
    frappe.call({
        method: "reckon_constructions.constructions.dashboard.get_project_dashboard",
        args: { construction_project: project },
    }).then((response) => {
        const data = response.message;
        const metrics = data.metrics;
        $(page.body).html(`
            <div class="row">
                ${dashboard_card(__("Approved Value"), format_currency(metrics.approved_value))}
                ${dashboard_card(__("Certified Value"), format_currency(metrics.certified_value))}
                ${dashboard_card(__("Completion"), `${format_number(metrics.completion_percent, 2)}%`)}
                ${dashboard_card(__("Forecast Margin"), format_currency(metrics.forecast_margin))}
            </div>
            <div class="row mt-4">
                <div class="col-md-6"><div class="frappe-card p-4"><h5>${__("Approvals")}</h5><p>${__("BOQ")}: ${frappe.utils.escape_html(data.approvals.boq)}</p><p>${__("Baseline")}: ${frappe.utils.escape_html(data.approvals.baseline)}</p></div></div>
                <div class="col-md-6"><div class="frappe-card p-4"><h5>${__("Open Controls")}</h5><p>${__("Issues")}: ${data.open_issues}</p><p>${__("RFIs")}: ${data.open_rfis}</p></div></div>
            </div>
        `);
    });
};

function dashboard_card(label, value) {
    return `<div class="col-md-3"><div class="frappe-card p-4"><div class="text-muted">${label}</div><div class="h3 mt-2">${value}</div></div></div>`;
}
