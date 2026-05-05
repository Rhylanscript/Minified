# utils/warnings.py

import warnings
import functools

# helper decorator to show error in console when deprecated function used
# work out how to integrate into intellisense
def deprecated(func: function) -> None:
    
    @functools.wraps(func)
    def new_func(*args, **kwargs) -> function:
        warnings.warn(
            f"Call to deprecated function {func.__name__}.",
            category = DeprecationWarning,
            stacklevel = 2
        )
        return func(*args, **kwargs)
    return new_func