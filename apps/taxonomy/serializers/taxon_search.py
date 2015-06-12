from django.core.paginator import Paginator, EmptyPage

from haystack.query import SearchQuerySet

from rest_framework import serializers


class BaseSearchSerializer(serializers.Serializer):
    search_query = serializers.CharField(required=True)
    page = serializers.CharField(required=False, default=1)
    ordering = serializers.CharField(required=False, default='ordering_name')
    pagination = serializers.IntegerField(required=False, default=10)
    filter_type = serializers.CharField(required=False, default='contains')

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        super(BaseSearchSerializer, self).__init__(*args, **kwargs)

    def search(self):
        """
        Basic search by 'search_query' parameter. Orders and paginates
        the results
        """
        if self.data['filter_type'] == 'exact':
            model_query_set = SearchQuerySet().models(self.model).filter(
                content__exact=self.data['search_query'])
        elif self.data['filter_type'] == 'startswith':
            model_query_set = SearchQuerySet().models(self.model).filter(
                content__startswith=self.data['search_query'])
        else:
            model_query_set = SearchQuerySet().models(self.model).filter(
                content=self.data['search_query'])
        all_results = model_query_set

        filtered_results = self.filter_results(all_results)
        paginator = Paginator(filtered_results, self.data['pagination'])

        try:
            page = paginator.page(self.data['page'])
        except EmptyPage:
            return {"results": "None"}

        return self.search_result_to_json(page.object_list, len(filtered_results))

    def search_result_to_json(self, search_query_set, count):
        """
        Returns the entire search result as json
        """
        result_json = []
        for result in search_query_set:
            result_json.append(self.search_object_to_json(result))
        return {"results": result_json, "count": count}

    @staticmethod
    def search_object_to_json(result):
        """
        Converts a single search result object into json
        """
        jason = {
            "id": result.pk,
            "name": u'%s' % result.text[:-1],
            "full_taxon_name": result.full_taxon_name,
        }
        return jason

    def filter_results(self, search_queryset):
        """
        Filter the search results
        """
        filtered_results = search_queryset
        return filtered_results.order_by(self.data['ordering'])


class CommonNameSearchSerializer(serializers.Serializer):
    search_query = serializers.CharField(required=True)
    page = serializers.CharField(required=False, default=1)
    ordering = serializers.CharField(required=False, default='ordering_name')
    pagination = serializers.IntegerField(required=False, default=10)
    filter_type = serializers.CharField(required=False, default='contains')

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        super(CommonNameSearchSerializer, self).__init__(*args, **kwargs)

    def search(self):
        """
        Basic search by 'search_query' parameter. Orders and paginates
        the results
        """
        if self.data['filter_type'] == 'exact':
            model_query_set = SearchQuerySet().models(self.model).filter(
                content__exact=self.data['search_query'])
        elif self.data['filter_type'] == 'startswith':
            model_query_set = SearchQuerySet().models(self.model).filter(
                content__startswith=self.data['search_query'])
        else:
            model_query_set = SearchQuerySet().models(self.model).filter(
                content=self.data['search_query'])
        all_results = model_query_set

        filtered_results = self.filter_results(all_results)
        paginator = Paginator(filtered_results, self.data['pagination'])

        try:
            page = paginator.page(self.data['page'])
        except EmptyPage:
            return {"results": "None"}

        return self.search_result_to_json(page.object_list, len(filtered_results))

    def search_result_to_json(self, search_query_set, count):
        """
        Returns the entire search result as json
        """
        result_json = []
        for result in search_query_set:
            result_json.append(self.search_object_to_json(result))
        return {"results": result_json, "count": count}

    @staticmethod
    def search_object_to_json(result):
        """
        Converts a single search result object into json
        """
        jason = {
            "id": result.pk,
            "name": u'%s' % result.text[:-1],
            "taxon_id": result.taxon_id,
            "iso_639": result.iso_639
        }
        return jason

    def filter_results(self, search_queryset):
        """
        Filter the search results
        """
        filtered_results = search_queryset
        return filtered_results.order_by(self.data['ordering'])
