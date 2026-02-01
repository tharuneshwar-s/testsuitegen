# examples.py
# Collection of example functions demonstrating various Python type annotations
# From simple to complex, showcasing different data types and patterns

from typing import List, Dict, Union, Optional, Tuple, Set, FrozenSet, Any, Callable


# Example 1: Simple function with basic types
def example_1_simple_function(name: str, age: int) -> str:
    """Simple function with basic types."""
    return f"Hello {name}, you are {age} years old."


# Example 2: Function with optional parameters
def example_2_optional_function(name: str, age: Optional[int] = None) -> str:
    """Function with optional parameter."""
    if age:
        return f"Hello {name}, you are {age} years old."
    return f"Hello {name}."


# Example 3: Function with list
def example_3_list_function(items: List[str]) -> int:
    """Function that takes a list and returns its length."""
    return len(items)


# Example 4: Function with dictionary
def example_4_dict_function(data: Dict[str, int]) -> List[str]:
    """Function that processes a dictionary."""
    return [f"{k}: {v}" for k, v in data.items()]


# Example 5: Function with union types
def example_5_union_function(value: Union[str, int]) -> str:
    """Function that accepts string or int."""
    return str(value)


# Example 6: Function with tuple
def example_6_tuple_function(coords: Tuple[float, float]) -> float:
    """Function that calculates distance from origin."""
    x, y = coords
    return (x**2 + y**2) ** 0.5


# Example 7: Function with set
def example_7_set_function(tags: Set[str]) -> int:
    """Function that returns number of unique tags."""
    return len(tags)


# Example 8: Function with complex nested types
def example_8_complex_function(
    user: Dict[str, Union[str, int]],
    scores: List[Dict[str, float]],
    metadata: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """Complex function with nested types."""
    result = {
        "user": user,
        "average_score": (
            sum(score["value"] for score in scores) / len(scores) if scores else 0
        ),
        "metadata": metadata or {},
    }
    return result


# Example 9: Function with callable
def example_9_callback_function(
    data: List[int], processor: Callable[[int], int]
) -> List[int]:
    """Function that applies a callback to each item."""
    return [processor(item) for item in data]


# Example 10: Function with all basic types
def example_10_all_types_function(
    s: str, i: int, f: float, b: bool, bt: bytes
) -> Tuple[str, int, float, bool, str]:
    """Function demonstrating all basic Python types."""
    return s, i, f, b, bt.decode("utf-8")


# Example 11: Function with mutable defaults (should warn)
def example_11_mutable_defaults_function(
    items: List[int] = [], config: Dict[str, str] = {}
) -> Dict[str, Any]:
    """Function with mutable defaults - should generate warnings."""
    items.append(len(config))
    config["processed"] = "true"
    return {"items": items, "config": config}


# Example 12: Function with advanced unions
def example_12_advanced_union_function(
    value: Union[str, int, float, bool, None],
) -> str:
    """Function with union of multiple types including None."""
    if value is None:
        return "None"
    return f"Value: {value} (type: {type(value).__name__})"


# Example 13: Function with generic types
def example_13_generic_function(
    data: List[Dict[str, Union[int, str]]], mapping: Dict[str, Callable[[Any], Any]]
) -> List[Dict[str, Any]]:
    """Function with complex generic types."""
    result = []
    for item in data:
        processed = {}
        for key, value in item.items():
            if key in mapping:
                processed[key] = mapping[key](value)
            else:
                processed[key] = value
        result.append(processed)
    return result


# Example 14: Function with frozenset
def example_14_frozenset_function(tags: FrozenSet[str]) -> List[str]:
    """Function that works with frozenset."""
    return sorted(list(tags))


# Example 15: Function with variable-length tuple
def example_15_var_tuple_function(coords: Tuple[float, ...]) -> float:
    """Function with variable-length tuple."""
    return sum(x**2 for x in coords) ** 0.5


# Example 16: Extremely complex function
def example_16_extremely_complex_function(
    # Basic and collections (required)
    name: str,
    scores: List[float],
    metadata: Dict[str, Union[str, int, List[str]]],
    data: List[Dict[str, Union[int, str, List[Union[int, str]]]]],
    # Sets and tuples (with defaults)
    tags: Set[str] = set(),
    coordinates: Tuple[float, float, float] = (0.0, 0.0, 0.0),
    # Advanced types (optional)
    callback: Optional[Callable[[Dict[str, Any]], bool]] = None,
    config: Optional[Dict[str, Any]] = None,
    # Any and unions
    extra: Any = None,
    status: Union[str, int, None] = None,
) -> Dict[str, Union[str, float, List[Any], Dict[str, Any], Any]]:
    """Extremely complex function with all possible type constructs."""
    result = {
        "name": name,
        "average_score": sum(scores) / len(scores) if scores else 0,
        "metadata": metadata,
        "data_count": len(data),
        "unique_tags": len(tags),
        "distance": sum(x**2 for x in coordinates) ** 0.5,
        "extra": extra,
        "status": status,
    }

    if callback and config:
        result["validated"] = callback(config)

    return result


# Example 17: Function with class method (for testing self parameter)
class ExampleClass:
    def example_17_method_with_self(self, value: str) -> str:
        """Method that includes self parameter."""
        return f"Processed: {value}"


# Example 18: Function with *args and **kwargs (though not fully typed)
def example_18_args_kwargs_function(*args: int, **kwargs: str) -> Dict[str, Any]:
    """Function with *args and **kwargs."""
    return {"args_count": len(args), "kwargs": kwargs, "args_sum": sum(args)}


# Example 19: Recursive type (simulated with Any)
def example_19_recursive_function(data: Dict[str, Any]) -> Dict[str, Any]:
    """Function that could handle recursive structures."""
    # In practice, recursive types are hard to define in typing

    def r(d):
        if d == 0 or d == 1:
            return 1
        return r(d - 1) + r(d - 2)

    return r(data)


# Example 20: Function with literal types (using Union as approximation)
def example_20_literal_like_function(mode: Union[str, int]) -> str:
    """Function with literal-like types."""
    if isinstance(mode, str):
        return f"String mode: {mode}"
    return f"Int mode: {mode}"


# Example 21: Enum Definition
import enum


class Color(enum.Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


# Example 22: Dataclass Definition
from dataclasses import dataclass


@dataclass
class UserInfo:
    id: int
    username: str
    email: str
    is_active: bool = True


# Example 23: Pydantic Model
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    tags: List[str]


if __name__ == "__main__":
    try:
        from testsuitegen.src.parsers.python_parser.parser import parse_python_function
    except ImportError:
        # Fallback if running from the directory itself (not recommended due to name conflict with stdlib parser)
        from parser import parse_python_function

    # Test all examples
    examples = [
        ("simple_function", example_1_simple_function),
        ("optional_function", example_2_optional_function),
        ("list_function", example_3_list_function),
        ("dict_function", example_4_dict_function),
        ("union_function", example_5_union_function),
        ("tuple_function", example_6_tuple_function),
        ("set_function", example_7_set_function),
        ("complex_function", example_8_complex_function),
        ("callback_function", example_9_callback_function),
        ("all_types_function", example_10_all_types_function),
        ("mutable_defaults_function", example_11_mutable_defaults_function),
        ("advanced_union_function", example_12_advanced_union_function),
        ("generic_function", example_13_generic_function),
        ("frozenset_function", example_14_frozenset_function),
        ("var_tuple_function", example_15_var_tuple_function),
        ("extremely_complex_function", example_16_extremely_complex_function),
        ("method_with_self", ExampleClass().example_17_method_with_self),
        ("args_kwargs_function", example_18_args_kwargs_function),
        ("recursive_function", example_19_recursive_function),
        ("literal_like_function", example_20_literal_like_function),
        ("color_enum", Color),
        ("user_info_dataclass", UserInfo),
        ("product_model", Product),
    ]


def run_examples():
    """Run all examples and print results."""
    import json
    from .parser import parse_python_function

    for name, func in examples:
        try:
            parsed = parse_python_function(func)
            print(f"\n=== {name} ===")
            print(json.dumps(parsed, indent=2))
        except Exception as e:
            print(f"\n=== {name} ===")
            print(f"Error parsing {name}: {e}")


if __name__ == "__main__":
    run_examples()
