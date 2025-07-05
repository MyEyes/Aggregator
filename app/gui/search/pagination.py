from .filtering import FilterOptionKind, FilterOption, Filter
from sqlalchemy import desc, asc

class PaginationOptionKind(FilterOptionKind):
    def __init__(self):
        super().__init__("pagination")

    def create(self, options):
        return PaginationOption(options)
    
class PaginationOption(FilterOption):
    def __init__(self, options):
        super().__init__(options)
        self.order_idx = 20
        self.page = int(options.get("page", 1))
        self.per_page = int(options.get("perpage", 20))

    def apply(self, filter:Filter):
        pagination = filter.query.paginate(page=self.page, per_page=self.per_page, error_out=False)
        self.total = pagination.total
        filter.options_dict["pagination"] = {"page":self.page, "per_page":self.per_page, "total":self.total}
        filter.query = pagination