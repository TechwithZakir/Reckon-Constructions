from dataclasses import dataclass


@dataclass(frozen=True)
class RateComponentInput:
    quantity_factor: float
    unit_rate: float
    wastage_percent: float = 0


@dataclass(frozen=True)
class RateSummary:
    direct_cost: float
    overhead_amount: float
    markup_amount: float
    proposed_rate: float


def calculate_component_amount(component):
    quantity_factor = float(component.quantity_factor or 0)
    unit_rate = float(component.unit_rate or 0)
    wastage_percent = float(component.wastage_percent or 0)
    return quantity_factor * unit_rate * (1 + wastage_percent / 100)


def calculate_rate_summary(components, overhead_percent=0, markup_percent=0):
    direct_cost = sum(calculate_component_amount(component) for component in components)
    overhead_amount = direct_cost * float(overhead_percent or 0) / 100
    cost_with_overhead = direct_cost + overhead_amount
    markup_amount = cost_with_overhead * float(markup_percent or 0) / 100

    return RateSummary(
        direct_cost=direct_cost,
        overhead_amount=overhead_amount,
        markup_amount=markup_amount,
        proposed_rate=cost_with_overhead + markup_amount,
    )
