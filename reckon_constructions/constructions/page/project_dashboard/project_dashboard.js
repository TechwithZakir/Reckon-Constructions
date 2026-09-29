frappe.pages["project-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("Project Dashboard"),
        single_column: true,
    });

    ensure_dashboard_styles();
    const route_options = frappe.route_options || {};
    const initial_project = route_options.project || route_options.construction_project || "";
    $(page.body).html(`<div class="construction-dashboard text-muted p-4">${__("Loading projects...")}</div>`);

    frappe.call({
        method: "reckon_constructions.constructions.dashboard.get_dashboard_projects",
    }).then((response) => {
        const projects = (response.message && response.message.projects) || [];
        const selected = projects.some((project) => project.name === initial_project)
            ? initial_project
            : "";
        render_dashboard_shell(page, projects, selected);
        load_dashboard(page, selected);
    }).catch((error) => render_dashboard_error(page, error));
};

function render_dashboard_shell(page, projects, selected) {
    const project_options = projects.map((project) => {
        const label = [project.project_name || project.name, project.customer_name || project.customer].filter(Boolean).join(" · ");
        return `<option value="${escape_attr(project.name)}" ${project.name === selected ? "selected" : ""}>${escape_html(label)}</option>`;
    }).join("");
    $(page.body).html(`
        <div class="construction-dashboard">
            <div class="dashboard-toolbar frappe-card p-4 mb-4">
                <div>
                    <div class="text-muted small">${__("Construction controls")}</div>
                    <h3 class="mb-1">${__("Project performance dashboard")}</h3>
                    <div class="text-muted">${__("Monitor delivery, site activity, commercial exposure, and unresolved controls.")}</div>
                </div>
                <div class="dashboard-toolbar-actions">
                    <select class="form-control" data-dashboard-project ${projects.length ? "" : "disabled"}>
                        <option value="">${__("All projects - portfolio view")}</option>
                        ${project_options || `<option value="">${__("No projects available")}</option>`}
                    </select>
                    <button class="btn btn-default" data-dashboard-refresh>${__("Refresh")}</button>
                </div>
            </div>
            <div data-dashboard-content></div>
        </div>
    `);
    const body = $(page.body);
    body.find("[data-dashboard-project]").on("change", function () {
        load_dashboard(page, this.value);
    });
    body.find("[data-dashboard-refresh]").on("click", () => load_dashboard(page, body.find("[data-dashboard-project]").val()));
}

function load_dashboard(page, project) {
    $(page.body).find("[data-dashboard-content]").html(`<div class="text-muted p-4">${__("Loading analytics...")}</div>`);
    frappe.call({
        method: "reckon_constructions.constructions.dashboard.get_project_dashboard",
        args: project ? { project } : {},
    }).then((response) => {
        render_dashboard(page, response.message || {});
    }).catch((error) => render_dashboard_error(page, error));
}

function render_dashboard(page, data) {
    const metrics = data.metrics || {};
    const counts = data.counts || {};
    const currency = data.currency || "BDT";
    const scope_label = data.scope === "project" ? __("Selected project") : __("Portfolio overview");
    const project_label = data.project ? find_project_label(page, data.project) : __("All projects");
    const content = $(page.body).find("[data-dashboard-content]");
    content.html(`
        <div class="dashboard-scope mb-3"><strong>${escape_html(scope_label)}</strong><span>${escape_html(project_label)}</span></div>
        <div class="row dashboard-card-row">
            ${dashboard_card(__("Projects"), dashboard_number(counts.projects), "blue")}
            ${dashboard_card(__("Active"), dashboard_number(counts.active_projects), "green")}
            ${dashboard_card(__("Completed"), dashboard_number(counts.completed_projects), "teal")}
            ${dashboard_card(__("On hold"), dashboard_number(counts.on_hold_projects), "orange")}
            ${dashboard_card(__("Open issues"), dashboard_number(counts.open_issues), "red")}
            ${dashboard_card(__("Open RFIs"), dashboard_number(counts.open_rfis), "purple")}
        </div>
        <div class="row dashboard-card-row mt-2">
            ${dashboard_card(__("Approved value"), dashboard_currency(metrics.approved_value, currency), "blue", "col-xl-3 col-md-6")}
            ${dashboard_card(__("Certified value"), dashboard_currency(metrics.certified_value, currency), "green", "col-xl-3 col-md-6")}
            ${dashboard_card(__("Committed procurement"), dashboard_currency(metrics.committed_cost, currency), "orange", "col-xl-3 col-md-6")}
            ${dashboard_card(__("Completion"), dashboard_percent(metrics.completion_percent), "teal", "col-xl-3 col-md-6")}
        </div>
        <div class="row mt-4">
            <div class="col-xl-8 mb-4">${project_progress_panel(data.project_progress || [], currency)}</div>
            <div class="col-xl-4 mb-4">${status_panel(data.status_breakdown || {})}</div>
        </div>
        <div class="row">
            <div class="col-xl-7 mb-4">${site_report_panel(data.site_report_progress || [])}</div>
            <div class="col-xl-5 mb-4">${issue_panel(data.issue_summary || {}, counts)}</div>
        </div>
        <div class="row">
            <div class="col-xl-8 mb-4">${gantt_panel(data.gantt || [])}</div>
            <div class="col-xl-4 mb-4">${activity_panel(data.activity_summary || {}, data.approvals || {})}</div>
        </div>
        <div class="row">
            <div class="col-xl-8 mb-4">${recent_activity_panel(data.recent_activity || [])}</div>
            <div class="col-xl-4 mb-4">${report_links_panel()}</div>
        </div>
    `);
}

function find_project_label(page, project) {
    const option = $(page.body).find(`[data-dashboard-project] option[value="${escape_attr(project)}"]`);
    return option.length ? option.text() : project;
}

function dashboard_card(label, value, tone, column = "col-xl-2 col-md-4 col-6") {
    return `<div class="${column} mb-3"><div class="dashboard-card dashboard-card-${tone}"><div class="text-muted small">${escape_html(label)}</div><div class="dashboard-card-value">${escape_html(value)}</div></div></div>`;
}

function project_progress_panel(rows, currency) {
    const visible = rows.slice(0, 12);
    const body = visible.length ? visible.map((row) => `
        <div class="dashboard-progress-row">
            <div class="dashboard-progress-label"><span>${escape_html(row.project_name)}</span><strong>${dashboard_percent(row.progress)}</strong></div>
            <div class="dashboard-progress-track"><span style="width:${Math.min(100, Math.max(0, Number(row.progress) || 0))}%"></span></div>
            <div class="dashboard-progress-meta"><span>${escape_html(row.customer || "")}</span><span>${dashboard_currency(row.contract_value, currency)}</span></div>
        </div>
    `).join("") : empty_panel_message(__("No project progress data available."));
    return panel(__("Project-wise progress"), `<div class="text-muted small mb-3">${__("Top projects by reported completion")}</div>${body}`);
}

function site_report_panel(rows) {
    const visible = rows.slice(0, 10);
    const body = visible.length ? visible.map((row) => `
        <div class="dashboard-progress-row">
            <div class="dashboard-progress-label"><span>${escape_html(row.project_name)}</span><strong>${dashboard_percent(row.progress)}</strong></div>
            <div class="dashboard-progress-track dashboard-progress-track-teal"><span style="width:${Math.min(100, Math.max(0, Number(row.progress) || 0))}%"></span></div>
            <div class="dashboard-progress-meta"><span>${escape_html(row.report_date || "")}</span><span>${escape_html(row.status || "Draft")}</span></div>
        </div>
    `).join("") : empty_panel_message(__("No site reports available."));
    return panel(__("Site report progress"), `<div class="text-muted small mb-3">${__("Latest verified site visits and reported completion")}</div>${body}`);
}

function status_panel(statuses) {
    const total = Object.values(statuses).reduce((sum, value) => sum + Number(value || 0), 0);
    const body = Object.entries(statuses).map(([status, value]) => {
        const percent = total ? Number(value) / total * 100 : 0;
        return `<div class="dashboard-status-row"><span>${escape_html(status)}</span><strong>${dashboard_number(value)}</strong><div class="dashboard-progress-track"><span style="width:${percent}%"></span></div></div>`;
    }).join("") || empty_panel_message(__("No status data available."));
    return panel(__("Project status mix"), `<div class="text-muted small mb-3">${__("Current delivery position across the portfolio")}</div>${body}`);
}

function issue_panel(summary, counts) {
    const status = summary.status || {};
    const severity = summary.severity || {};
    const status_html = Object.entries(status).map(([key, value]) => `<div class="dashboard-kpi-line"><span>${escape_html(key)}</span><strong>${dashboard_number(value)}</strong></div>`).join("");
    const severity_html = Object.entries(severity).map(([key, value]) => `<div class="dashboard-kpi-line"><span>${escape_html(key)} severity</span><strong>${dashboard_number(value)}</strong></div>`).join("");
    return panel(__("Issues and resolution"), `
        <div class="dashboard-mini-heading">${__("Status")}</div>${status_html || empty_panel_message(__("No issues recorded."))}
        <div class="dashboard-mini-heading mt-3">${__("Severity")}</div>${severity_html || empty_panel_message(__("No severity data."))}
        <div class="dashboard-callout mt-3"><strong>${dashboard_number(counts.resolved_issues)}</strong> ${__("issues resolved or closed")}</div>
    `);
}

function gantt_panel(rows) {
    const visible = rows.slice(0, 16);
    if (!visible.length) return panel(__("Project Gantt schedule"), empty_panel_message(__("No task schedule available.")));
    const dates = visible.flatMap((row) => [row.start_date, row.end_date]).filter(Boolean).map((value) => new Date(value));
    const min_date = Math.min(...dates);
    const max_date = Math.max(...dates);
    const span = Math.max(max_date - min_date, 86400000);
    const body = visible.map((row) => {
        const start = row.start_date ? new Date(row.start_date).getTime() : min_date;
        const end = row.end_date ? new Date(row.end_date).getTime() : start + 86400000;
        const left = Math.max(0, (start - min_date) / span * 100);
        const width = Math.max(2, Math.min(100 - left, (end - start) / span * 100));
        return `<div class="dashboard-gantt-row"><div class="dashboard-gantt-label"><span>${escape_html(row.subject)}</span><small>${escape_html(row.project_name)}</small></div><div class="dashboard-gantt-track"><span style="left:${left}%;width:${width}%"><i style="width:${Math.min(100, Math.max(0, Number(row.progress) || 0))}%"></i></span></div><strong>${dashboard_percent(row.progress)}</strong></div>`;
    }).join("");
    return panel(__("Project Gantt schedule"), `<div class="text-muted small mb-3">${__("Planned task dates with current completion")}</div>${body}`);
}

function activity_panel(summary, approvals) {
    const rows = [
        [__("Tasks"), summary.tasks],
        [__("Site visits"), summary.site_visits],
        [__("Issues"), summary.issues],
        [__("RFIs"), summary.rfis],
        [__("Engineering documents"), summary.engineering_documents],
        [__("Progress certificates"), summary.certificates],
    ];
    return panel(__("Project activity"), `${rows.map(([label, value]) => `<div class="dashboard-kpi-line"><span>${escape_html(label)}</span><strong>${dashboard_number(value)}</strong></div>`).join("")}<div class="dashboard-mini-heading mt-3">${__("Approval controls")}</div><div class="dashboard-kpi-line"><span>${__("BOQ")}</span><strong>${escape_html(approvals.boq || "Missing")}</strong></div><div class="dashboard-kpi-line"><span>${__("Baseline")}</span><strong>${escape_html(approvals.baseline || "Missing")}</strong></div><div class="dashboard-callout mt-3"><strong>${dashboard_number(approvals.pending)}</strong> ${__("records awaiting review")}</div>`);
}

function recent_activity_panel(rows) {
    const body = rows.length ? `<div class="table-responsive"><table class="table table-sm mb-0"><thead><tr><th>${__("Activity")}</th><th>${__("Project")}</th><th>${__("Date")}</th><th>${__("Status")}</th></tr></thead><tbody>${rows.map((row) => `<tr><td><strong>${escape_html(row.type)}</strong><div class="text-muted small">${escape_html(row.name)}</div></td><td>${escape_html(row.project || "")}</td><td>${escape_html(String(row.date || "").slice(0, 10))}</td><td>${escape_html(row.status || "Draft")}</td></tr>`).join("")}</tbody></table></div>` : empty_panel_message(__("No recent activity available."));
    return panel(__("Recent activity and visits"), body);
}

function report_links_panel() {
    return panel(__("Decision reports"), `
        <div class="dashboard-report-link" data-report="Project Progress Summary">${__("Project-wise progress report")}<span>›</span></div>
        <div class="dashboard-report-link" data-report="Site Progress Activity">${__("Site report activity report")}<span>›</span></div>
        <div class="dashboard-report-link" data-report="Project Gantt Schedule">${__("Project Gantt schedule report")}<span>›</span></div>
        <div class="dashboard-report-link" data-report="Project Activity and Issues">${__("Activity, visits, issues and resolution")}<span>›</span></div>
        <div class="text-muted small mt-3">${__("Use the reports for export, filtering, and management review.")}</div>
    `);
}

function panel(title, content) {
    return `<div class="frappe-card dashboard-panel"><div class="dashboard-panel-header"><h4>${escape_html(title)}</h4></div><div class="dashboard-panel-body">${content}</div></div>`;
}

function empty_panel_message(message) {
    return `<div class="text-muted small py-3">${escape_html(message)}</div>`;
}

function dashboard_number(value, decimals = 0) {
    const number = Number(value || 0);
    return Number.isFinite(number) ? number.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) : "0";
}

function dashboard_percent(value) {
    return `${dashboard_number(value, 1)}%`;
}

function dashboard_currency(value, currency) {
    const number = Number(value || 0);
    if (!Number.isFinite(number)) return "0";
    try {
        return new Intl.NumberFormat("en-BD", { style: "currency", currency: currency || "BDT", maximumFractionDigits: 2 }).format(number);
    } catch (error) {
        return `${escape_html(currency || "BDT")} ${dashboard_number(number, 2)}`;
    }
}

function render_dashboard_error(page, error) {
    const message = error && error.message ? error.message : __("Unable to load the project dashboard.");
    $(page.body).html(`<div class="alert alert-danger m-4">${escape_html(message)}</div>`);
}

function escape_html(value) {
    return frappe.utils.escape_html(String(value == null ? "" : value));
}

function escape_attr(value) {
    return escape_html(value).replace(/"/g, "&quot;");
}

function ensure_dashboard_styles() {
    if (document.getElementById("construction-dashboard-styles")) return;
    $("<style id='construction-dashboard-styles'>").text(`
        .construction-dashboard { padding-bottom: 32px; }
        .dashboard-toolbar { display:flex; justify-content:space-between; gap:24px; align-items:flex-end; }
        .dashboard-toolbar-actions { display:flex; gap:8px; min-width:360px; }
        .dashboard-scope { display:flex; gap:12px; align-items:center; color:var(--text-muted); }
        .dashboard-scope span { color:var(--text-color); }
        .dashboard-card { border:1px solid var(--border-color); border-left:4px solid var(--blue-500); border-radius:8px; background:var(--card-bg); padding:16px; min-height:86px; }
        .dashboard-card-green { border-left-color:var(--green-500); }
        .dashboard-card-teal { border-left-color:var(--teal-500); }
        .dashboard-card-orange { border-left-color:var(--orange-500); }
        .dashboard-card-red { border-left-color:var(--red-500); }
        .dashboard-card-purple { border-left-color:var(--purple-500); }
        .dashboard-card-value { color:var(--text-color); font-size:20px; font-weight:600; margin-top:8px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
        .dashboard-panel { height:100%; overflow:hidden; }
        .dashboard-panel-header { border-bottom:1px solid var(--border-color); padding:16px 20px; }
        .dashboard-panel-header h4 { margin:0; font-size:15px; }
        .dashboard-panel-body { padding:16px 20px; }
        .dashboard-progress-row { margin-bottom:15px; }
        .dashboard-progress-label, .dashboard-progress-meta, .dashboard-kpi-line { display:flex; justify-content:space-between; gap:12px; align-items:center; }
        .dashboard-progress-label { font-size:13px; margin-bottom:6px; }
        .dashboard-progress-meta { color:var(--text-muted); font-size:11px; margin-top:5px; }
        .dashboard-progress-track { background:var(--gray-200); border-radius:4px; height:7px; overflow:hidden; }
        .dashboard-progress-track span { background:var(--blue-500); display:block; height:100%; border-radius:4px; }
        .dashboard-progress-track-teal span { background:var(--teal-500); }
        .dashboard-status-row { display:grid; grid-template-columns:1fr auto; gap:6px 12px; align-items:center; margin-bottom:13px; font-size:13px; }
        .dashboard-status-row .dashboard-progress-track { grid-column:1 / -1; }
        .dashboard-kpi-line { border-bottom:1px solid var(--border-color); padding:8px 0; font-size:13px; }
        .dashboard-kpi-line:last-child { border-bottom:0; }
        .dashboard-mini-heading { color:var(--text-muted); font-size:11px; font-weight:600; text-transform:uppercase; letter-spacing:.04em; }
        .dashboard-callout { background:var(--subtle-fg); border-radius:6px; color:var(--text-muted); padding:10px 12px; font-size:12px; }
        .dashboard-callout strong { color:var(--text-color); font-size:16px; margin-right:4px; }
        .dashboard-gantt-row { display:grid; grid-template-columns:190px 1fr 48px; gap:12px; align-items:center; margin-bottom:12px; font-size:12px; }
        .dashboard-gantt-label { overflow:hidden; }
        .dashboard-gantt-label span, .dashboard-gantt-label small { display:block; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
        .dashboard-gantt-label small { color:var(--text-muted); margin-top:2px; }
        .dashboard-gantt-track { background:var(--gray-200); height:13px; border-radius:4px; position:relative; overflow:hidden; }
        .dashboard-gantt-track > span { background:var(--blue-400); border-radius:4px; height:100%; position:absolute; top:0; min-width:5px; overflow:hidden; }
        .dashboard-gantt-track i { background:var(--green-500); display:block; height:100%; }
        .dashboard-report-link { border-bottom:1px solid var(--border-color); cursor:pointer; display:flex; justify-content:space-between; padding:11px 0; font-size:13px; }
        .dashboard-report-link:hover { color:var(--primary); }
        .dashboard-report-link span { font-size:18px; line-height:12px; }
        @media (max-width: 768px) { .dashboard-toolbar { display:block; } .dashboard-toolbar-actions { min-width:0; margin-top:16px; } .dashboard-gantt-row { grid-template-columns:125px 1fr 42px; gap:8px; } }
    `).appendTo("head");
    $(document).off("click.constructionDashboard", "[data-report]").on("click.constructionDashboard", "[data-report]", function () {
        frappe.set_route("query-report", $(this).data("report"));
    });
}
