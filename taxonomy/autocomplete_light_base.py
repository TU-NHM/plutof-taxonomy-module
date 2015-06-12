import autocomplete_light


class BaseAutocomplete(autocomplete_light.AutocompleteModelBase):
    model = None
    permission = ''

    def choices_for_values(self):
        """
        Used to avoid 'invalid literal for int() with base 10'
        error
        """
        try:
            return super(autocomplete_light.AutocompleteModelBase, self).choices_for_values()
        except ValueError:
            return []

    def choices_for_request(self):
        """
        Returns choices for autocomplete fields.
        """
        self.choices = self.model.objects.all()
        return super(BaseAutocomplete, self).choices_for_request()
