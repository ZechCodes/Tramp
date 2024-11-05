try:
    from annotationlib import get_annotations, Format, ForwardRef
except ImportError:
    from ._annotations import get_annotations, Format, ForwardRef
