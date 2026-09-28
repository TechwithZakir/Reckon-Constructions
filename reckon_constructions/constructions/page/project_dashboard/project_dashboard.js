frappe.pages["project-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Project Dashboard"),
        single_column: true,
    });

    const route_options = frappe.route_options || {};
    const initial_project = route_options.construction_project || "";
    $(page.body).html(`<div class="construction-dashboard text-muted">${__("Loading projects...")}</div>`);

    frappe.call({
        method: "reckon_constructions.constructions.dashboard.get_dashboard_projects",
    }).then((response) => {
        const projects = (response.message && response.message.projects) || [];
        const selected = projects.some((project) => project.name === initial_project)
            ? initial_project
            : projects[0] && projects[0].name;
        render_dashboard_shell(page, projects, selected);
        if (selected) load_dashboard(page, selected);
    }).catch((error) => render_dashboard_error(page, error));
};

function render_dashboard_shell(page, projects, selected) {
    const project_options = projects.map((project) => {
        const label = [project.project || project.name, project.customer].filter(Boolean).join(" · ");
        return `<option value="${frappe.utils.escape_html(project.name)}" ${project.name === selected ? "selected" : ""}>${frappe.utils.escape_html(label)}</option>`;
    }).join("");
    const empty_state = projects.length ? "" : `<div class="text-muted">${__("Create a Construction Project to start using the dashboard.")}</div>`;
    $(page.body).html(`
        <div class="frappe-card p-4 mb-4">
            <div class="row align-items-end">
                <div class="col-md-8">
                    <label class="control-label">${__("Construction Project")}</label>
                    <select class="form-control" data-dashboard-project ${projects.length ? "" : "disabled"}>
                        ${project_options || `<option value="">${__("No projects available")}</option>`}
                    </select>
                </div>
                <div class="col-md-4 text-muted small">${__("Select a project to view commercial, progress, and control metrics.")}</div>
            </div>
        </div>
        ${empty_state}
        <div data-dashboard-content></div>
    `);
    $(page.body).find("[data-dashboard-project]").on("change", function () {
        load_dashboard(page, this.value);
    });
}

function load_dashboard(page, project) {
    if (!project) return;
    $(page.body).find("[data-dashboard-content]").html(`<div class="text-muted">${__("Loading dashboard...")}</div>`);
    frappe.call({
        method: "reckon_constructions.constructions.dashboard.get_project_dashboard",
        args: { construction_project: project },
    }).then((response) => {
        const data = response.message;
        const metrics = data.metrics;
        $(page.body).find("[data-dashboard-content]").html(`
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
    }).catch((error) => render_dashboard_error(page, error));
}

function render_dashboard_error(page, error) {
    const message = error && error.message ? error.message : __("Unable to load the project dashboard.");
    $(page.body).html(`<div class="alert alert-danger">${frappe.utils.escape_html(message)}</div>`);
}

function dashboard_card(label, value) {
    return `<div class="col-md-3"><div class="frappe-card p-4"><div class="text-muted">${label}</div><div class="h3 mt-2">${value}</div></div></div>`;
}
