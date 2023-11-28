from ..models.tag import Tag
from sqlalchemy import desc, asc

class FilterSort:
    @classmethod 
    def filterFromRequest(cls, request, filterTarget, tagTarget=None):
        if "search" in request.args:
            _search = request.args["search"]
            filtered = filterTarget.search(_search)
        else:
            filtered = filterTarget.query

        _filter_tags = None
        if "filter_tags" in request.args:
            _filter_tags = request.args["filter_tags"]
            if isinstance(_filter_tags, int):
                _filter_tags = [_filter_tags]
            if isinstance(_filter_tags, str):
                if len(_filter_tags)>0:
                    _filter_tags = _filter_tags.split(',')
                else:
                    _filter_tags = []
            if len(_filter_tags)>0:
                if not tagTarget:
                    filtered = filtered.filter(filterTarget.tags.any(Tag.id.in_(_filter_tags)))
                else:
                    filtered = filtered.filter(tagTarget.any(Tag.id.in_(_filter_tags)))
        if _filter_tags and len(_filter_tags)>0:
            filter_tags = Tag.query.filter(Tag.id.in_(_filter_tags))
        else:
            filter_tags = []

        _sort_op = "desc"
        if "sort_op" in request.args:
            _sort_op = request.args["sort_op"]
        _sort = filterTarget._defaultSort
        if "sort" in request.args:
            _sort = request.args['sort']
            __sort = _sort
            if _sort_op == "asc":
                filtered = filtered.order_by(asc(__sort))
            else:
                filtered = filtered.order_by(desc(__sort))
        _page = 1
        if "page" in request.args:
            _page = int(request.args['page'])

        filterInfo = {'filter_tags': filter_tags, 'sort_op': _sort_op, 'sort': _sort, 'page': _page}
        filtered = filtered.paginate(page=_page, per_page=20, error_out=False)
        return filterInfo, filtered