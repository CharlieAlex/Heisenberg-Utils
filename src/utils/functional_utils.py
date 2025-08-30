from collections.abc import Callable
from functools import partial, reduce


def compose(*funcs: Callable) -> Callable:
    """Functional composition utility.

    Usage
    ---
    - compose(f, g, h)(x) == f(g(h(x)))
    - [f, g, h] will be f(g(h(x)))

    Returns
    ---
    A function that is the composition of the input functions.
    """
    def compose_two(f, g):
        return lambda x: f(g(x))
    return reduce(compose_two, funcs)


def format_partial_object(p_obj: partial|Callable) -> str:
    """Format a partial object into a string representation.

    Args
    ---
    p_obj (partial|Callable): The partial object or callable to format.

    Returns
    ---
    str: A string representation of the partial object or callable.
    """
    if not isinstance(p_obj, partial):
        if hasattr(p_obj, "__name__"):
            return p_obj.__name__ + "()"
        elif hasattr(p_obj, "__class__") and hasattr(p_obj.__class__, "__name__"):
            return p_obj.__class__.__name__ + "()"
        else:
            return str(p_obj)

    func_name = p_obj.func.__name__

    args_list = [repr(arg) for arg in p_obj.args]

    kwargs_list = [f"{k}={repr(v)}" for k, v in (p_obj.keywords or {}).items()]

    all_args_str = ", ".join(args_list + kwargs_list)

    return f"{func_name}({all_args_str})"
