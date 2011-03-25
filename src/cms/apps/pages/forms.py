"""Forms used by the CMS."""


from django import forms


class PageFormBase(forms.ModelForm):
    
    """Form used to edit Page models."""
    
    def clean_permalink(self):
        """"Ensures that the permalink is None, or unique."""
        value = self.cleaned_data["permalink"]
        instance = self.instance
        model = instance.__class__
        # Null values are okay.
        if not value:
            return value
        # Check that non-null permalinks are unique.
        try:
            other = model.objects.get_page(value)
            if other != instance:
                raise forms.ValidationError("Page with this permalink already exists.")
        except model.DoesNotExist:
            pass
        # Check that permalinks do not start with a number.
        try:
            int(value[0])
        except ValueError:
            pass
        else:
            raise forms.ValidationError("A permalink cannot start with a number.")
        # All good!
        return value