import functools
import inspect


def validate_range(param_name, min_value, max_value):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()  # ensures default values fill in

            if param_name not in bound_args.arguments:
                # At this point, if the parameter is truly missing
                # this error will be raised.
                raise ValueError(f"Parameter '{param_name}' is missing.")

            value = bound_args.arguments[param_name]
            if min_value is not None and value < min_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be at least {min_value}."
                )
            if max_value is not None and value > max_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be at most {max_value}."
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def greater_than(param_name, min_value):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()  # ensures default values fill in

            if param_name not in bound_args.arguments:
                # At this point, if the parameter is truly missing
                # this error will be raised.
                raise ValueError(f"Parameter '{param_name}' is missing.")

            value = bound_args.arguments[param_name]
            if min_value is not None and value < min_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be at least {min_value}."
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def less_than(param_name, max_value):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()  # ensures default values fill in

            if param_name not in bound_args.arguments:
                # At this point, if the parameter is truly missing
                # this error will be raised.
                raise ValueError(f"Parameter '{param_name}' is missing.")

            value = bound_args.arguments[param_name]
            if max_value is not None and value > max_value:
                raise ValueError(
                    f"Parameter '{param_name}' must be at most {max_value}."
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
