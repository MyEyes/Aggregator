from .filtering import FilterOptionKind, FilterOption, Filter
from ...models.tag import Tag

class TagFilterOptionKind(FilterOptionKind):
    def __init__(self):
        super().__init__("tag_filter")

    def create(self, options):
        return TagFilterOption(options)
    
class TagFilterOption(FilterOption):
    def __init__(self, options):
        super().__init__(options)
        self.raw_option = options.get("tags", None)
        self.filter_tags = []
        if self.raw_option:
            if isinstance(self.raw_option, int):
                self.filter_tags = [self.raw_option]
                self.raw_option = [self.raw_option]
            elif isinstance(self.raw_option, str):
                if len(self.raw_option)>0:
                    self.filter_tags = self.raw_option.split(',')
                else:
                    self.filter_tags = []
            elif isinstance(self.raw_option, list):
                self.filter_tags = self.raw_option
        self.order_idx = 1
            

    def apply(self, filter:Filter):
        if len(self.filter_tags)>0:
            if not filter.tag_target:
                for tag_id in self.filter_tags:
                    filter.query = filter.query.filter(filter.target.tags.any(Tag.id==tag_id))
            else:
                for tag_id in self.filter_tags:
                    filter.query = filter.query.filter(filter.tag_target.any(Tag.id==tag_id))
            filter.filter_tags = Tag.query.filter(Tag.id.in_(self.filter_tags))
            filter.options_dict["tag_filter"] = {"tags": self.filter_tags}
        else:
            filter.filter_tags = []
        