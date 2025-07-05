from .filtering import FilterOptionKind, FilterOption, Filter

class SearchOptionKind(FilterOptionKind):
    def __init__(self):
        super().__init__("search")

    def create(self, options):
        return SearchOption(options)
    
class SearchOption(FilterOption):
    def __init__(self, options):
        super().__init__(options)
        self.search_term = options.get("term", None)
        self.order_idx = 0

    def apply(self, filter:Filter):
        if self.search_term:
            filter.query = filter.target.search(self.search_term)