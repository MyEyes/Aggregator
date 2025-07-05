from .filtering import FilterOptionKind, FilterOption, Filter
from sqlalchemy import desc, asc

class OrderOptionKind(FilterOptionKind):
    def __init__(self):
        super().__init__("order")

    def create(self, options):
        return OrderOption(options)
    
class OrderOption(FilterOption):
    def __init__(self, options):
        super().__init__(options)
        self.ordering = options.get("ordering", "asc")
        self.ordering_func = asc if self.ordering == "asc" else desc
        self.order_by = options.get("order_by", "id")
        self.order_idx = 3
            

    def apply(self, filter:Filter):
        filter.query = filter.query.order_by(self.ordering_func(self.order_by))