import ast
import operator
from dataclasses import dataclass


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


@dataclass(frozen=True)
class CalculationResult:
    result: float
    explanation: str


def calculate_formula(formula, variables):
    if not formula:
        _throw("A calculation formula is required.")

    clean_variables = {key: float(value or 0) for key, value in variables.items()}
    try:
        expression = ast.parse(formula, mode="eval")
    except SyntaxError:
        _throw("Formula syntax is invalid.")
    result = _evaluate_node(expression.body, clean_variables)
    explanation = _build_explanation(formula, clean_variables, result)
    return CalculationResult(result=result, explanation=explanation)


def _evaluate_node(node, variables):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)

    if isinstance(node, ast.Name):
        if node.id not in variables:
            _throw(f"Formula variable {node.id} is not declared.")
        return variables[node.id]

    if isinstance(node, ast.BinOp):
        operator_fn = ALLOWED_OPERATORS.get(type(node.op))
        if not operator_fn:
            _throw("Formula uses an unsupported operator.")
        left = _evaluate_node(node.left, variables)
        right = _evaluate_node(node.right, variables)
        if isinstance(node.op, ast.Div) and right == 0:
            _throw("Formula cannot divide by zero.")
        return operator_fn(left, right)

    if isinstance(node, ast.UnaryOp):
        operator_fn = ALLOWED_UNARY_OPERATORS.get(type(node.op))
        if not operator_fn:
            _throw("Formula uses an unsupported unary operator.")
        return operator_fn(_evaluate_node(node.operand, variables))

    _throw("Formula contains an unsafe or unsupported expression.")


def _build_explanation(formula, variables, result):
    variable_text = ", ".join(f"{key}={value:g}" for key, value in sorted(variables.items()))
    return f"{formula} with {variable_text} = {result:g}"


def _throw(message):
    try:
        import frappe
    except ModuleNotFoundError as error:
        raise ValueError(message) from error

    frappe.throw(message)
