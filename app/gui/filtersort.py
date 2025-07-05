from .search import Filter
import json

class FilterSort:
    @classmethod 
    def filterFromRequest(cls, request, filterTarget, tagTarget=None):
        options_str = request.args.get("filter", None)
        if options_str:
            options = json.loads(options_str)
        else:
            options = {}
        filter = Filter(filterTarget, options, tagTarget)
        return filter, filter.query