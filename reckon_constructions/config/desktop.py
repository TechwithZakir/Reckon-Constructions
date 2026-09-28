from frappe import _


def get_data():
    return [
        {
            "module_name": "Constructions",
            "category": "Modules",
            "label": _("Constructions"),
            "color": "#0f766e",
            "icon": "octicon octicon-tools",
            "type": "module",
            "description": _("Construction project management"),
        }
    ]
