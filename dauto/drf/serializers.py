import typing
from rest_framework import serializers

# Some times we want to sort the fields of a serializer alphabetically to make it easier to read

class AlphaSortedFieldsSerializer(serializers.Serializer):
    """
    Serializer that sorts fields alphabetically. Order first 'url' and 'id' fields typically resources identifiers
    """

    sorted_first_fields: typing.Iterable[str] = ("url", "id")

    def sort_fields(self, representation: typing.Dict[str, typing.Any]) -> dict:
        """
        Sort representation keys alphabetically.
        Place first those fields in sorted_first_fields prop, by default identity fields ('id' and 'url')
        and last meta fields (starting with '_')


        :param representation: default
        :return: sorted dict
        """

        # Sort the fields alphabetically by key
        sorted_representation = OrderedDict(sorted(representation.items()))

        # Extract sorted fists fields
        sorted_first_dict = {
            field: sorted_representation.pop(field)
            for field in self.sorted_first_fields
            if field in sorted_representation
        }

        # Extract meta fields
        meta_fields_dict = {
            field: sorted_representation.get(field)
            for field in representation
            if field.startswith("_") or field == "meta"
        }

        if sorted_first_dict:
            sorted_representation = {**sorted_first_dict, **sorted_representation}

        if meta_fields_dict:
            for field in meta_fields_dict:
                sorted_representation.pop(field)
            sorted_representation = {**sorted_representation, **meta_fields_dict}

        return sorted_representation

    def to_representation(self, instance):
        return self.sort_fields(super().to_representation(instance))