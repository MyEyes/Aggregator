import json
class Filter:
    def __init__(self, filterTarget, options_dict, tagTarget=None):
        self.target = filterTarget
        self.query = self.target.query
        self.tag_target = tagTarget
        self.page = 0
        self.filter_tags = []
        try:
            self.options_dict = options_dict
            if not self.options_dict:
                self.options_dict = {}
            self.options = []
            self._create_options()
            self.apply_options(self.options)
        except Exception as e:
            print(e)
            self.options_dict = {}
            self.options = []

    def _create_options(self):
        for key,val in self.options_dict.items():
            self.options.append(FilterOptionKind.from_options(key, val))
        self.options.sort(key=lambda option: option.order_idx)

    def apply_options(self, options):
        for option in options:
            option.apply(self)

    def as_json(self):
        return json.dumps(self.options_dict)

    def get_query(self):
        return self.query


class FilterOptionKind:
    class_dict = {}

    def __init__(self, name):
        self.name = name

    def __init_subclass__(cls):
        super().__init_subclass__()
        inst = cls()
        FilterOptionKind.class_dict[inst.name] = inst

    def create(self, options:dict) -> "FilterOption":
        pass
    
    @classmethod
    def from_options(self, key:str, options:dict):
        key_inst = FilterOptionKind.class_dict.get(key)
        if not key_inst:
            raise Exception(f"Unknown option kind: {key}")
        return key_inst.create(options)

class FilterOption:
    def __init__(self, options):
        self.options = options

    def apply(self, filter:Filter):
        pass