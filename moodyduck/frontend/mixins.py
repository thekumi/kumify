"""
Bootstrap 5 form mixin.

Automatically applies the correct Bootstrap 5 CSS class to every widget in a
form so that `{{ field }}` renders a properly-styled input without any extra
template work.
"""

# Maps Django widget class names → Bootstrap 5 CSS class
_WIDGET_CLASSES = {
    "TextInput": "form-control",
    "EmailInput": "form-control",
    "URLInput": "form-control",
    "NumberInput": "form-control",
    "PasswordInput": "form-control",
    "Textarea": "form-control",
    "DateInput": "form-control",
    "DateTimeInput": "form-control",
    "TimeInput": "form-control",
    "SplitDateTimeWidget": "form-control",
    "Select": "form-select",
    "SelectMultiple": "form-select",
    "CheckboxInput": "form-check-input",
    "FileInput": "form-control",
    "ClearableFileInput": "form-control",
    # Intentionally no class for hidden / multi-hidden inputs
    "HiddenInput": "",
    "MultipleHiddenInput": "",
}


class BootstrapMixin:
    """
    Mix this in *before* ModelForm / Form in the MRO:

        class MyForm(BootstrapMixin, ModelForm):
            ...

    It calls super().__init__() first so that all fields are fully initialised
    before the classes are injected, which means __init__ overrides in
    subclasses (e.g. narrowing a queryset) work as expected.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            # Unwrap MultiWidget children too (e.g. SplitDateTimeWidget)
            widgets = getattr(widget, "widgets", None)
            targets = list(widgets) if widgets else [widget]
            for w in targets:
                cls = _WIDGET_CLASSES.get(w.__class__.__name__, "form-control")
                if not cls:
                    continue
                existing = w.attrs.get("class", "")
                # Avoid duplicating the class if already present
                if cls not in existing.split():
                    w.attrs["class"] = f"{existing} {cls}".strip()
