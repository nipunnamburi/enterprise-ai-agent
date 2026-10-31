import ast
import operator
import math
from typing import Dict, Any, Union
from app.tools.base import BaseTool

# Safe AST operators map
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

SAFE_FUNCTIONS = {
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "sum": sum,
    "sqrt": math.sqrt,
    "ceil": math.ceil,
    "floor": math.floor,
}

def safe_eval_ast(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")
    elif isinstance(node, ast.BinOp):
        left = safe_eval_ast(node.left)
        right = safe_eval_ast(node.right)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported binary operator: {op_type.__name__}")
    elif isinstance(node, ast.UnaryOp):
        operand = safe_eval_ast(node.operand)
        op_type = type(node.op)
        if op_type in SAFE_OPERATORS:
            return SAFE_OPERATORS[op_type](operand)
        raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in SAFE_FUNCTIONS:
            func = SAFE_FUNCTIONS[node.func.id]
            args = [safe_eval_ast(arg) for arg in node.args]
            return func(*args)
        raise ValueError(f"Unsupported function call in expression: {ast.dump(node)}")
    else:
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

class CalculatorTool(BaseTool):
    name = "calculator"
    description = (
        "Performs exact, deterministic mathematical calculations such as percentages, "
        "refund calculations, differences, growth rates, restocking fee deductions, and averages. "
        "Never perform math via LLM hallucination when this tool is available."
    )
    category = "computation"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Mathematical expression to compute, e.g., '(2499.00 * 0.85)', '((720000 - 650000) / 650000) * 100', or '149.99 * 3'."
                },
                "operation_type": {
                    "type": "string",
                    "enum": ["custom_expression", "refund_calculation", "percentage_difference", "growth_rate", "average"],
                    "description": "Optional calculation mode helper."
                }
            },
            "required": ["expression"]
        }

    def run(self, expression: str, operation_type: str = "custom_expression", **kwargs) -> Dict[str, Any]:
        clean_expr = expression.strip()
        try:
            parsed = ast.parse(clean_expr, mode='eval')
            result = safe_eval_ast(parsed.body)
            
            # Format number nicely if float
            formatted_result = result
            if isinstance(result, float):
                formatted_result = round(result, 4)
                if formatted_result.is_integer():
                    formatted_result = int(formatted_result)

            return {
                "success": True,
                "expression": expression,
                "result": formatted_result,
                "operation_type": operation_type,
                "formatted_output": f"{expression} = {formatted_result}"
            }
        except Exception as e:
            return {
                "success": False,
                "expression": expression,
                "error": f"Math calculation failed: {str(e)}"
            }

calculator_tool = CalculatorTool()
