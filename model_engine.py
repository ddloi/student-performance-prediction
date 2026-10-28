"""Compatibility for legacy imports and saved model_engine pickle references.

Runtime implementation lives in student_performance. Keep this module so the
existing model cache remains readable without retraining or rewriting it.
"""

from student_performance.models import LinearRegressionScratch


def __getattr__(name):
    from student_performance import engine as runtime

    if name == "engine":
        return runtime.get_engine()
    try:
        return getattr(runtime, name)
    except AttributeError:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from None
