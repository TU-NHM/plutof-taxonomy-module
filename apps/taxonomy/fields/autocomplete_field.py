from django.core.urlresolvers import reverse, get_script_prefix

import autocomplete_light

from rest_framework.relations import HyperlinkedRelatedField


class AutocompleteHyperlinkedRelatedField(HyperlinkedRelatedField):
    """
    Used in hyperlinked autocomplete fields. Converts the 'id' or
    full url path of the object into resolvable url.
    Otherwise acts as a regular HyperlinkedRelatedField
    """
    def __init__(self, *args, **kwargs):
        autocomplete_class = kwargs.pop('autocomplete_class', None)
        if not autocomplete_class:
            queryset = kwargs.get('queryset', None)
            if queryset:
                autocomplete_class = '%sAutocomplete' % queryset.model.__name__
        if autocomplete_class:
            kwargs["widget"] = autocomplete_light.ChoiceWidget(autocomplete_class)
        super(AutocompleteHyperlinkedRelatedField, self).__init__(*args, **kwargs)

    def from_native(self, value):
        if value.isdigit():
            # Convert pk to url
            value = reverse(self.view_name, args=[int(value)])
            prefix = get_script_prefix()
            if value.startswith(prefix):
                # Remove unnecessary prefixes from url
                value = '/' + value[len(prefix):]

        return super(AutocompleteHyperlinkedRelatedField, self).from_native(value)
