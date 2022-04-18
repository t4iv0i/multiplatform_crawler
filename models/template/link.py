from .template import Template


class Link(Template):
    fields = {
        "database": {"type": "str"},
        "collection": {"type": "str"},
        "id": {"type": "str"},
    }

    def __new__(cls, *args, **kwargs):
        return Template.__new__(cls, Class=Template, database='template', collection='Link')