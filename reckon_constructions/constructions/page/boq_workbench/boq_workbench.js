frappe.pages["boq-workbench"].on_page_load = function (wrapper) {
    new BOQWorkbench(wrapper);
};

class BOQWorkbench {
    constructor(wrapper) {
        this.page = frappe.ui.make_app_page({
            parent: wrapper,
            title: __("BOQ Workbench"),
            single_column: true,
        });
        this.state = {
            name: "",
            projects: [],
            items: [],
            templates: [],
            uoms: [],
            sections: [],
            lines: [],
            project: "",
            customer: "",
            company: "",
            currency: "",
            boq_type: "Construction",
            revision_no: 1,
            revision_reason: "",
        };
        this.inject_styles();
        this.load_context();
    }

    load_context() {
        const route_options = frappe.route_options || {};
        frappe.call({
            method: "reckon_constructions.constructions.boq_workbench.get_boq_workbench_context",
            args: { boq: route_options.boq || route_options.construction_boq || "" },
        }).then((response) => {
            const context = response.message || {};
            this.state.projects = context.projects || [];
            this.state.items = context.items || [];
            this.state.templates = context.templates || [];
            this.state.uoms = context.uoms || [];
            if (context.boq) {
                this.load_boq(context.boq);
            } else {
                const selected = route_options.construction_project || (this.state.projects[0] && this.state.projects[0].name);
                this.select_project(selected);
                this.state.sections = [{ section_code: "01", section_name: __("General Works"), description: "" }];
            }
            this.render();
        }).catch((error) => {
            this.page.body.html(`<div class="alert alert-danger">${this.escape(error.message || __("Unable to load the BOQ workbench."))}</div>`);
        });
    }

    load_boq(boq) {
        this.state.name = boq.name || "";
        this.state.project = boq.project || "";
        this.state.customer = boq.customer || "";
        this.state.company = boq.company || "";
        this.state.currency = boq.currency || "";
        this.state.boq_type = boq.boq_type || "Construction";
        this.state.revision_no = boq.revision_no || 1;
        this.state.revision_reason = boq.revision_reason || "";
        this.state.sections = boq.sections || [];
        this.state.lines = (boq.items || []).map((line) => ({ ...line }));
    }

    select_project(name) {
        const project = this.state.projects.find((row) => row.name === name);
        this.state.project = name || "";
        this.state.customer = project ? project.customer || "" : "";
        this.state.company = project ? project.company || "" : "";
        this.state.currency = project ? project.currency || "" : "";
    }

    render() {
        const s = this.state;
        this.page.body.html(`
            <div class="boq-workbench">
                <div class="boq-toolbar">
                    <div>
                        <div class="text-muted small">${__("Engineer-friendly BOQ entry")}</div>
                        <h3 class="mb-1">${__("Construction BOQ")}</h3>
                        <div class="text-muted small">${s.name ? this.escape(s.name) : __("New draft")}</div>
                    </div>
                    <div class="boq-toolbar-actions">
                        <button class="btn btn-default" data-action="open-list">${__("BOQ List")}</button>
                        <button class="btn btn-default" data-action="new">${__("New BOQ")}</button>
                        <button class="btn btn-primary" data-action="save">${__("Save Draft")}</button>
                    </div>
                </div>

                <div class="boq-help-strip">
                    <strong>${__("Quick workflow")}</strong>
                    <span>${__("Choose the project, add sections, enter line items, and use Measure for length × width × height quantities. Calculation Templates keep repeated formulas consistent.")}</span>
                    <button class="btn btn-link btn-sm" data-action="templates">${__("View calculation templates")}</button>
                </div>

                <div class="frappe-card p-4 mb-4">
                    <div class="boq-section-heading"><h5>${__("Project and commercial details")}</h5><span class="text-muted small">${__("These values are copied from the Construction Project.")}</span></div>
                    <div class="row">
                        ${this.field("project", __("Project"), this.project_options(), "select", true)}
                        ${this.field("customer", __("Customer"), s.customer, "text", false, true)}
                        ${this.field("company", __("Company"), s.company, "text", false, true)}
                        ${this.field("currency", __("Currency"), s.currency, "text", false, true)}
                        ${this.field("boq_type", __("BOQ Type"), this.select_options(["Construction", "Tender", "Variation"], s.boq_type), "select")}
                        ${this.field("revision_no", __("Revision"), s.revision_no, "number")}
                    </div>
                    <div class="row">
                        <div class="col-md-8">
                            <label class="control-label">${__("Revision reason")}</label>
                            <input class="form-control" data-field="revision_reason" value="${this.escape(s.revision_reason)}" placeholder="${__("Optional: describe what changed")}">
                        </div>
                    </div>
                </div>

                <div class="frappe-card mb-4">
                    <div class="boq-table-header">
                        <div><h5 class="mb-1">${__("Sections and line items")}</h5><span class="text-muted small">${s.lines.length} ${__("line items")}</span></div>
                        <div class="boq-toolbar-actions">
                            <button class="btn btn-default btn-sm" data-action="add-section">${__("Add Section")}</button>
                            <button class="btn btn-primary btn-sm" data-action="add-line">${__("Add Line Item")}</button>
                        </div>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-bordered boq-lines-table mb-0">
                            <thead><tr><th class="boq-number">#</th><th>${__("Work item / specification")}</th><th>${__("Qty")}</th><th>${__("UOM")}</th><th>${__("Rate")}</th><th>${__("Amount")}</th><th>${__("Measurement")}</th><th></th></tr></thead>
                            <tbody>${this.render_rows()}</tbody>
                        </table>
                    </div>
                    <div class="boq-total-row"><span>${__("BOQ Total")}</span><strong data-total>${this.format_total()}</strong></div>
                </div>
            </div>
        `);
        this.bind_events();
    }

    render_rows() {
        if (!this.state.sections.length) {
            return `<tr><td colspan="8" class="text-muted text-center p-4">${__("Add a section to start building the BOQ.")}</td></tr>`;
        }
        let number = 0;
        return this.state.sections.map((section, section_index) => {
            const lines = this.state.lines
                .map((line, index) => ({ line, index }))
                .filter(({ line }) => line.section === section.section_name);
            const section_total = lines.reduce((sum, { line }) => sum + this.amount(line), 0);
            const section_row = `
                <tr class="boq-section-row">
                    <td>${this.escape(section.section_code || String(section_index + 1).padStart(2, "0"))}</td>
                    <td colspan="5"><input class="form-control form-control-sm section-name" data-section-index="${section_index}" value="${this.escape(section.section_name)}" placeholder="${__("Section name")}"></td>
                    <td class="text-right font-weight-bold">${this.format_currency(section_total)}</td>
                    <td class="text-nowrap"><button class="btn btn-link btn-sm" data-action="add-line-section" data-section-index="${section_index}" title="${__("Add line to this section")}">+ ${__("line")}</button><button class="btn btn-link btn-sm text-danger" data-action="remove-section" data-section-index="${section_index}" title="${__("Remove section")}">×</button></td>
                </tr>`;
            const line_rows = lines.length
                ? lines.map(({ line, index }) => this.render_line(line, index, ++number)).join("")
                : `<tr><td></td><td colspan="7" class="text-muted small py-3">${__("No line items yet. Add a line to this section.")}</td></tr>`;
            return section_row + line_rows;
        }).join("");
    }

    render_line(line, index, number) {
        const amount = this.amount(line);
        return `
            <tr data-line-index="${index}">
                <td class="text-muted">${number}</td>
                <td class="boq-item-cell">
                    <select class="form-control form-control-sm mb-2" data-line-field="item_code">${this.item_options(line.item_code)}</select>
                    <input class="form-control form-control-sm" data-line-field="description" value="${this.escape(line.description || "")}" placeholder="${__("Describe the work item")}">
                    ${line.measurement_ref ? `<div class="text-muted small mt-1">${this.escape(line.measurement_ref)}</div>` : ""}
                </td>
                <td><input class="form-control form-control-sm text-right" data-line-field="quantity" type="number" min="0" step="0.001" value="${line.quantity || 0}"></td>
                <td><select class="form-control form-control-sm" data-line-field="uom">${this.uom_options(line.uom)}</select></td>
                <td><input class="form-control form-control-sm text-right" data-line-field="rate" type="number" min="0" step="0.01" value="${line.rate || 0}"></td>
                <td class="text-right font-weight-bold line-amount">${this.format_currency(amount)}</td>
                <td><button class="btn btn-default btn-sm" data-action="measure" data-line-index="${index}">${__("Measure")}</button></td>
                <td><button class="btn btn-link btn-sm text-danger" data-action="remove-line" data-line-index="${index}" title="${__("Remove line")}">×</button></td>
            </tr>`;
    }

    bind_events() {
        const body = this.page.body;
        body.find("[data-field='project']").on("change", (event) => {
            this.select_project(event.currentTarget.value);
            this.render();
        });
        body.find("[data-field='boq_type']").on("change", (event) => { this.state.boq_type = event.currentTarget.value; });
        body.find("[data-field='revision_no']").on("change", (event) => { this.state.revision_no = event.currentTarget.value; });
        body.find("[data-field='revision_reason']").on("input", (event) => { this.state.revision_reason = event.currentTarget.value; });
        body.find(".section-name").on("change", (event) => {
            const index = Number(event.currentTarget.dataset.sectionIndex);
            const previous = this.state.sections[index].section_name;
            const value = event.currentTarget.value.trim() || previous;
            this.state.sections[index].section_name = value;
            this.state.lines.forEach((line) => { if (line.section === previous) line.section = value; });
            this.render();
        });
        body.find("[data-line-index]").each((_, row) => {
            const line_index = Number(row.dataset.lineIndex);
            $(row).find("[data-line-field]").on("input change", (event) => {
                const field = event.currentTarget.dataset.lineField;
                this.state.lines[line_index][field] = ["quantity", "rate"].includes(field)
                    ? Number(event.currentTarget.value || 0)
                    : event.currentTarget.value;
                this.update_line_total(row, this.state.lines[line_index]);
            });
        });
        body.find("[data-action]").on("click", (event) => this.handle_action(event.currentTarget));
    }

    handle_action(button) {
        const action = button.dataset.action;
        if (action === "add-section") this.add_section();
        if (action === "add-line") this.add_line();
        if (action === "add-line-section") this.add_line(Number(button.dataset.sectionIndex));
        if (action === "remove-section") this.remove_section(Number(button.dataset.sectionIndex));
        if (action === "remove-line") this.remove_line(Number(button.dataset.lineIndex));
        if (action === "measure") this.open_measurement(Number(button.dataset.lineIndex));
        if (action === "save") this.save();
        if (action === "new") this.new_boq();
        if (action === "open-list") frappe.set_route("boq-register");
        if (action === "templates") frappe.set_route("List", "Calculation Template");
    }

    add_section() {
        const index = this.state.sections.length + 1;
        this.state.sections.push({ section_code: String(index).padStart(2, "0"), section_name: __("New Section"), description: "" });
        this.render();
    }

    add_line(section_index) {
        if (!this.state.sections.length) this.add_section();
        const section = this.state.sections[section_index || 0].section_name;
        this.state.lines.push({ section, item_code: "", description: "", quantity: 0, uom: "", rate: 0, measurement_ref: "" });
        this.render();
    }

    remove_section(index) {
        const section = this.state.sections[index];
        if (!section) return;
        if (this.state.lines.some((line) => line.section === section.section_name)) {
            frappe.confirm(__("This section has line items. Remove the section and its lines?"), () => {
                this.state.sections.splice(index, 1);
                this.state.lines = this.state.lines.filter((line) => line.section !== section.section_name);
                this.render();
            });
            return;
        }
        this.state.sections.splice(index, 1);
        this.render();
    }

    remove_line(index) {
        this.state.lines.splice(index, 1);
        this.render();
    }

    open_measurement(index) {
        const line = this.state.lines[index];
        if (!this.state.templates.length) {
            frappe.msgprint(__("Create a Calculation Template first, then use Measure on a BOQ line."));
            return;
        }
        const dialog = new frappe.ui.Dialog({
            title: __("Measure quantity"),
            fields: [
                { fieldname: "template", label: __("Calculation Template"), fieldtype: "Select", options: this.state.templates.map((template) => template.name).join("\n"), reqd: 1 },
                { fieldname: "length", label: __("Length"), fieldtype: "Float", default: 1 },
                { fieldname: "width", label: __("Width"), fieldtype: "Float", default: 1 },
                { fieldname: "height", label: __("Height"), fieldtype: "Float", default: 1 },
                { fieldname: "count", label: __("Count"), fieldtype: "Float", default: 1 },
                { fieldname: "factor", label: __("Factor"), fieldtype: "Float", default: 1 },
            ],
            primary_action_label: __("Apply measurement"),
            primary_action: (values) => {
                const template = this.state.templates.find((row) => row.name === values.template);
                const quantity = calculate_measurement(template, values);
                line.quantity = quantity;
                line.uom = template.output_uom || line.uom;
                line.measurement_ref = `${template.template_name}: ${[values.length, values.width, values.height, values.count, values.factor].filter((value) => Number(value) !== 1).join(" × ") || "1"}`;
                dialog.hide();
                this.render();
            },
        });
        dialog.show();
    }

    save() {
        if (!this.state.project) {
            frappe.msgprint(__("Select a Construction Project before saving."));
            return;
        }
        frappe.call({
            method: "reckon_constructions.constructions.boq_workbench.save_boq_draft",
            args: { payload: JSON.stringify(this.build_payload()) },
            freeze: true,
            freeze_message: __("Saving BOQ draft...")
        }).then((response) => {
            const saved = response.message;
            this.state.name = saved.name;
            frappe.show_alert({ message: __("BOQ draft saved"), indicator: "green" });
            this.render();
        }).catch((error) => frappe.msgprint({ title: __("Unable to save BOQ"), message: error.message || __("Please check the required fields.") }));
    }

    new_boq() {
        frappe.confirm(__("Start a new BOQ draft? Unsaved changes will be cleared."), () => {
            const project = this.state.project;
            this.state = { ...this.state, name: "", sections: [{ section_code: "01", section_name: __("General Works"), description: "" }], lines: [], revision_no: 1, revision_reason: "" };
            this.select_project(project);
            this.render();
        });
    }

    build_payload() {
        return {
            name: this.state.name,
            project: this.state.project,
            customer: this.state.customer,
            company: this.state.company,
            currency: this.state.currency,
            boq_type: this.state.boq_type,
            revision_no: Number(this.state.revision_no || 1),
            revision_reason: this.state.revision_reason,
            sections: this.state.sections,
            items: this.state.lines,
        };
    }

    update_line_total(row, line) {
        $(row).find(".line-amount").text(this.format_currency(this.amount(line)));
        this.page.body.find("[data-total]").text(this.format_total());
    }

    amount(line) { return Number(line.quantity || 0) * Number(line.rate || 0); }
    format_total() { return this.format_currency(this.state.lines.reduce((sum, line) => sum + this.amount(line), 0)); }
    format_currency(value) { return format_currency(value || 0, this.state.currency || undefined); }
    format_number(value) { return Number(value || 0).toLocaleString(undefined, { maximumFractionDigits: 3 }); }
    escape(value) { return frappe.utils.escape_html(String(value == null ? "" : value)); }

    field(name, label, value, type, required, readonly) {
        const control = type === "select"
            ? `<select class="form-control" data-field="${name}" ${required ? "required" : ""}>${value}</select>`
            : `<input class="form-control" data-field="${name}" type="${type === "number" ? "number" : "text"}" value="${this.escape(value)}" ${readonly ? "readonly" : ""} ${required ? "required" : ""}>`;
        return `<div class="col-md-4"><label class="control-label">${label}${required ? " *" : ""}</label>${control}</div>`;
    }

    project_options() { return this.state.projects.map((project) => `<option value="${this.escape(project.name)}" ${project.name === this.state.project ? "selected" : ""}>${this.escape(project.project || project.name)}</option>`).join("") || `<option value="">${__("No projects available")}</option>`; }
    select_options(values, selected) { return values.map((value) => `<option value="${this.escape(value)}" ${value === selected ? "selected" : ""}>${this.escape(value)}</option>`).join(""); }
    item_options(selected) { return `<option value="">${__("Select item or describe below")}</option>` + this.state.items.map((item) => `<option value="${this.escape(item.name)}" ${item.name === selected ? "selected" : ""}>${this.escape(item.name + (item.item_name ? ` · ${item.item_name}` : ""))}</option>`).join(""); }
    uom_options(selected) { const values = [...new Set([selected, "m³", "m²", "m", "Nos", "kg", "lot", ...this.state.uoms.map((row) => row.name)].filter(Boolean))]; return this.select_options(values, selected); }

    inject_styles() {
        if (document.getElementById("boq-workbench-styles")) return;
        $(`<style id="boq-workbench-styles">
            .boq-workbench { max-width: 1500px; margin: 0 auto; }
            .boq-toolbar, .boq-table-header, .boq-section-heading, .boq-total-row { display:flex; align-items:center; justify-content:space-between; gap:16px; }
            .boq-toolbar { margin-bottom:20px; }
            .boq-toolbar-actions { display:flex; gap:8px; flex-wrap:wrap; }
            .boq-help-strip { border-left:3px solid var(--blue-500); background:var(--control-bg); padding:12px 16px; margin-bottom:20px; display:flex; gap:12px; align-items:center; flex-wrap:wrap; }
            .boq-lines-table { min-width:1000px; }
            .boq-lines-table th { white-space:nowrap; font-size:12px; color:var(--text-muted); }
            .boq-lines-table td { vertical-align:middle; }
            .boq-number { width:46px; }
            .boq-item-cell { min-width:300px; }
            .boq-section-row { background:var(--subtle-fg); }
            .boq-section-row .section-name { font-weight:600; }
            .boq-total-row { padding:16px 20px; background:var(--subtle-fg); }
            .boq-total-row strong { font-size:18px; }
            @media (max-width: 768px) { .boq-toolbar, .boq-table-header { align-items:flex-start; flex-direction:column; } }
        </style>`).appendTo("head");
    }
}

function calculate_measurement(template, values) {
    const length = Number(values.length || 0);
    const width = Number(values.width || 0);
    const height = Number(values.height || 0);
    const count = Number(values.count || 0);
    const factor = Number(values.factor || 0);
    const type = (template && template.measurement_type) || "Count";
    if (type === "Volume") return length * width * height * count * factor;
    if (type === "Area") return length * width * count * factor;
    if (type === "Length") return length * count * factor;
    if (type === "Factor") return count * factor;
    return count;
}
