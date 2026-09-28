frappe.pages["boq-register"].on_page_load = function (wrapper) {
    new BOQRegister(wrapper);
};

class BOQRegister {
    constructor(wrapper) {
        this.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: __("Construction BOQ"),
            single_column: true,
        });
        this.state = { search: "", status: "", page: 1, page_length: 20, total: 0, rows: [] };
        this.render_shell();
        this.bind_events();
        this.load();
    }

    render_shell() {
        this.page.set_primary_action(__("New Construction BOQ"), () => open_boq_workbench());
        this.page.add_inner_button(__("Refresh"), () => this.load());
        $(this.page.body).html(`
            <div class="boq-register">
                <div class="frappe-card p-4 mb-4">
                    <div class="d-flex justify-content-between align-items-start flex-wrap" style="gap: 16px;">
                        <div>
                            <h4 class="mb-1">${__("Construction BOQ register")}</h4>
                            <div class="text-muted">${__("Create, review, revise, and manage project bills of quantities from one place.")}</div>
                        </div>
                        <div class="boq-register-count text-muted small" data-count></div>
                    </div>
                    <div class="row mt-4 align-items-end">
                        <div class="col-md-8">
                            <label class="control-label">${__("Search BOQs")}</label>
                            <input class="form-control" data-search type="search" placeholder="${__("BOQ number, project, customer, or company")}">
                        </div>
                        <div class="col-md-4">
                            <label class="control-label">${__("Status")}</label>
                            <select class="form-control" data-status>
                                <option value="">${__("All statuses")}</option>
                                <option value="Draft">${__("Draft")}</option>
                                <option value="Under Review">${__("Under Review")}</option>
                                <option value="Approved">${__("Approved")}</option>
                                <option value="Superseded">${__("Superseded")}</option>
                                <option value="Cancelled">${__("Cancelled")}</option>
                            </select>
                        </div>
                    </div>
                </div>
                <div class="frappe-card">
                    <div class="table-responsive">
                        <table class="table table-hover mb-0">
                            <thead><tr>
                                <th>${__("BOQ")}</th><th>${__("Project")}</th><th>${__("Customer")}</th>
                                <th>${__("Revision")}</th><th>${__("Status")}</th><th class="text-right">${__("Total")}</th>
                                <th class="text-right">${__("Actions")}</th>
                            </tr></thead>
                            <tbody data-rows></tbody>
                        </table>
                    </div>
                    <div class="p-3 border-top d-flex justify-content-between align-items-center">
                        <span class="text-muted small" data-page-label></span>
                        <div>
                            <button class="btn btn-default btn-sm mr-2" data-prev>${__("Previous")}</button>
                            <button class="btn btn-default btn-sm" data-next>${__("Next")}</button>
                        </div>
                    </div>
                </div>
            </div>
        `);
    }

    bind_events() {
        const body = $(this.page.body);
        body.find("[data-search]").on("input", frappe.utils.debounce(() => {
            this.state.search = body.find("[data-search]").val();
            this.state.page = 1;
            this.load();
        }, 350));
        body.find("[data-status]").on("change", (event) => {
            this.state.status = event.currentTarget.value;
            this.state.page = 1;
            this.load();
        });
        body.find("[data-prev]").on("click", () => {
            if (this.state.page > 1) {
                this.state.page -= 1;
                this.load();
            }
        });
        body.find("[data-next]").on("click", () => {
            if (this.state.page * this.state.page_length < this.state.total) {
                this.state.page += 1;
                this.load();
            }
        });
        body.on("click", "[data-action]", (event) => {
            const button = event.currentTarget;
            const name = button.dataset.name;
            if (button.dataset.action === "open") open_boq_workbench(name);
            if (button.dataset.action === "delete") this.confirm_delete(name);
        });
    }

    load() {
        $(this.page.body).find("[data-rows]").html(`<tr><td colspan="7" class="text-muted text-center p-5">${__("Loading BOQs...")}</td></tr>`);
        frappe.call({
            method: "reckon_constructions.constructions.page.boq_register.boq_register.get_boq_register",
            args: {
                search: this.state.search,
                status: this.state.status,
                page: this.state.page,
                page_length: this.state.page_length,
            },
        }).then((response) => {
            const data = response.message || {};
            this.state.rows = data.rows || [];
            this.state.total = data.total || 0;
            this.render_rows();
        }).catch((error) => {
            const message = error && error.message ? error.message : __("Unable to load Construction BOQs.");
            $(this.page.body).find("[data-rows]").html(`<tr><td colspan="7" class="text-danger p-4">${frappe.utils.escape_html(message)}</td></tr>`);
        });
    }

    render_rows() {
        const body = $(this.page.body);
        body.find("[data-count]").text(__("{0} BOQ(s)", [this.state.total]));
        body.find("[data-page-label]").text(this.state.total ? __("Page {0}", [this.state.page]) : "");
        body.find("[data-prev]").prop("disabled", this.state.page <= 1);
        body.find("[data-next]").prop("disabled", this.state.page * this.state.page_length >= this.state.total);
        if (!this.state.rows.length) {
            body.find("[data-rows]").html(`<tr><td colspan="7" class="text-muted text-center p-5">${__("No BOQs match the selected filters.")}</td></tr>`);
            return;
        }
        body.find("[data-rows]").html(this.state.rows.map((row) => {
            const status_class = {
                Draft: "gray",
                "Under Review": "orange",
                Approved: "green",
                Superseded: "blue",
                Cancelled: "red",
            }[row.status] || "gray";
            const delete_button = row.status === "Draft"
                ? `<button class="btn btn-link btn-sm text-danger" data-action="delete" data-name="${escape_attr(row.name)}">${__("Delete")}</button>`
                : "";
            return `<tr>
                <td><button class="btn btn-link p-0 font-weight-bold" data-action="open" data-name="${escape_attr(row.name)}">${escape_html(row.name)}</button><div class="text-muted small">${escape_html(row.boq_type || __("Construction"))}</div></td>
                <td>${escape_html(row.project || "-")}</td>
                <td>${escape_html(row.customer || "-")}</td>
                <td>${escape_html(row.revision_no || "1")}</td>
                <td><span class="indicator-pill ${status_class}">${escape_html(row.status || __("Draft"))}</span></td>
                <td class="text-right">${escape_html(format_boq_total(row.total_amount, row.currency))}</td>
                <td class="text-right text-nowrap"><button class="btn btn-default btn-sm" data-action="open" data-name="${escape_attr(row.name)}">${__("Open / Edit")}</button>${delete_button}</td>
            </tr>`;
        }).join(""));
    }

    confirm_delete(name) {
        frappe.confirm(__("Delete draft BOQ {0}? This cannot be undone.", [name]), () => {
            frappe.call({
                method: "reckon_constructions.constructions.page.boq_register.boq_register.delete_boq",
                args: { name },
            }).then(() => {
                frappe.show_alert({ message: __("BOQ deleted"), indicator: "green" });
                this.load();
            });
        });
    }
}

function open_boq_workbench(boq) {
    frappe.route_options = boq ? { boq } : {};
    frappe.set_route("boq-workbench");
}

function escape_html(value) {
    return frappe.utils.escape_html(String(value == null ? "" : value));
}

function escape_attr(value) {
    return escape_html(value).replace(/"/g, "&quot;");
}

function format_boq_total(value, currency) {
    if (value == null || value === "") return "-";
    return format_currency(value, currency || undefined);
}
