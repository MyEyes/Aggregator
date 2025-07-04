class Breadcrumb:
    def __init__(self, text, url=None):
        self.text = text
        self.url = url

    def hasUrl(self):
        return self.url is not None