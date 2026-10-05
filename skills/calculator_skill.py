"""
Calculator & Unit Conversion Skill for Z.O.E.
==============================================
Demonstrates how a skill parses user input, performs safe computation,
and formats a clean voice-friendly response.
"""

import re
import ast
import operator
from typing import Dict, Any, Optional
from .base_skill import BaseSkill

# Supported mathematical operators
_SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def _safe_eval(node):
    """Safely evaluates an abstract syntax tree (AST) expression without using unsafe eval()."""
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Unsupported constant type")
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type in _SAFE_OPERATORS:
            left = _safe_eval(node.left)
            right = _safe_eval(node.right)
            return _SAFE_OPERATORS[op_type](left, right)
        raise ValueError(f"Unsupported operator: {op_type}")
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type in _SAFE_OPERATORS:
            return _SAFE_OPERATORS[op_type](_safe_eval(node.operand))
        raise ValueError(f"Unsupported unary operator: {op_type}")
    raise ValueError("Invalid math expression")


class CalculatorSkill(BaseSkill):
    name = "Calculator & Unit Converter"
    description = "Evaluates arithmetic calculations and common unit conversions (Celsius/Fahrenheit, km/miles)."
    triggers = [
        "calculate", "what is", "how much is", "convert",
        "+", "-", "*", "/", "divided by", "times", "plus", "minus",
        "celsius", "fahrenheit", "km to miles", "miles to km"
    ]
    author = "Z.O.E Core Team"
    version = "1.0.0"

    def can_handle(self, message: str) -> bool:
        msg = message.lower().strip()
        
        # Check for unit conversions
        if ("convert" in msg and any(u in msg for u in ["celsius", "fahrenheit", "km", "miles", "c to f", "f to c"])) or \
           any(phrase in msg for phrase in ["c to f", "f to c", "celsius to fahrenheit", "fahrenheit to celsius"]):
            return True
            
        # Check for arithmetic questions like "what is 15 * 8?" or "calculate 45 + 12"
        if ("what is" in msg or "calculate" in msg or "how much is" in msg) and \
           any(ch.isdigit() for ch in msg) and \
           any(op in msg for op in ["+", "-", "*", "/", "plus", "minus", "times", "divided by"]):
            return True
            
        return False

    def execute(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        msg = message.lower().strip()

        # 1. Temperature Conversion: Celsius <-> Fahrenheit
        c_to_f_match = re.search(r'([-\d.]+)\s*(?:degrees?\s*)?(?:c|celsius)\s*(?:to|in)\s*(?:f|fahrenheit)', msg)
        if c_to_f_match:
            try:
                c = float(c_to_f_match.group(1))
                f = (c * 9 / 5) + 32
                return f"{c:g} degrees Celsius is {f:g} degrees Fahrenheit."
            except Exception:
                pass

        f_to_c_match = re.search(r'([-\d.]+)\s*(?:degrees?\s*)?(?:f|fahrenheit)\s*(?:to|in)\s*(?:c|celsius)', msg)
        if f_to_c_match:
            try:
                f = float(f_to_c_match.group(1))
                c = (f - 32) * 5 / 9
                return f"{f:g} degrees Fahrenheit is {c:g} degrees Celsius."
            except Exception:
                pass

        # 2. Distance Conversion: km <-> miles
        km_to_mi_match = re.search(r'([\d.]+)\s*(?:km|kilometres?|kilometers?)\s*(?:to|in)\s*miles?', msg)
        if km_to_mi_match:
            try:
                km = float(km_to_mi_match.group(1))
                miles = km * 0.621371
                return f"{km:g} kilometers is approximately {miles:.2f} miles."
            except Exception:
                pass

        mi_to_km_match = re.search(r'([\d.]+)\s*miles?\s*(?:to|in)\s*(?:km|kilometres?|kilometers?)', msg)
        if mi_to_km_match:
            try:
                miles = float(mi_to_km_match.group(1))
                km = miles / 0.621371
                return f"{miles:g} miles is approximately {km:.2f} kilometers."
            except Exception:
                pass

        # 3. Arithmetic Evaluation
        clean_expr = msg
        for prefix in ["what is", "calculate", "how much is", "solve", "please", "can you"]:
            clean_expr = clean_expr.replace(prefix, "")

        clean_expr = clean_expr.replace("?", "").replace("!", "").strip()
        clean_expr = clean_expr.replace("times", "*").replace("multiplied by", "*")
        clean_expr = clean_expr.replace("divided by", "/").replace("over", "/")
        clean_expr = clean_expr.replace("plus", "+").replace("minus", "-")
        clean_expr = clean_expr.replace("x", "*").replace("^", "**")

        # Sanitize so only digits, decimals, operators, and parentheses remain
        sanitized = re.sub(r'[^0-9+\-*/(). ]', '', clean_expr).strip()
        if not sanitized:
            return "I couldn't detect a valid mathematical expression to calculate."

        try:
            tree = ast.parse(sanitized, mode='eval')
            result = _safe_eval(tree.body)
            # Format nicely (e.g. 24 instead of 24.0)
            if isinstance(result, float) and result.is_integer():
                result = int(result)
            elif isinstance(result, float):
                result = round(result, 4)
            return f"{sanitized} equals {result}."
        except ZeroDivisionError:
            return "Division by zero is undefined."
        except Exception as e:
            return f"I had trouble calculating that expression. Please check the format."
