from datetime import datetime, timezone
from dateutil.parser import parse
import re
from constant import constant


class Template:
    system = {
        "system_created_time": {
            "type": "datetime"
        },
        "system_updated_time": {
            "type": "datetime"
        }
    }

    Model = dict()

    def __new__(cls, *args, **kwargs):
        database = kwargs.get("database", "template")
        collection = kwargs.get("collection", "Template")
        Class = kwargs.get("Class", cls)
        if Class.Model.get(database):
            Class.Model[database][collection] = cls
        else:
            Class.Model[database] = {collection: cls}
        return object.__new__(cls)

    def __init__(self, *args, **kwargs):
        data = kwargs.get("data")
        if data:
            meta = getattr(self, 'meta')
            Class = self.Model[meta['db_alias']][meta['collection']]
            model_names = list(self.Model[meta['db_alias']].keys())
            fields = Class.get_fields()
            connections = Class.get_connections()
            for field, raw in data.items():
                if raw in [None, [], {}]:
                    continue
                if fields.get(field):
                    regex = re.findall(r'^(.+)<*(.*)>*', fields[field]["type"])
                    if len(regex) == 0:
                        continue
                    value = None
                    typ3, collections = regex[0]
                    if typ3 == "bool":
                        value = bool(raw)
                    elif re.match(r'int', typ3):
                        value = int(raw)
                    elif typ3 == "datetime":
                        try:
                            value = parse(raw)
                        except ValueError:
                            pass
                    elif typ3 == 'list':
                        for collection in collections.split(','):
                            if collection in model_names:
                                model = self.Model[meta['db_alias']][collection]
                                value = model(raw)
                                break
                    if value is None:
                        value = raw
                        # value = helper.remove_id(raw)
                    setattr(self, field, value)
                elif connections.get(field):
                    Link = self.Model["template"]["Link"]
                    value = Link(raw)
                    setattr(self, field, value)

    @classmethod
    def get_fields(cls):
        fields = dict()
        for typ3 in ["fields", "system"]:
            if hasattr(cls, typ3):
                obj = getattr(cls, typ3)
                fields.update(obj)
        return fields

    @classmethod
    def get_connections(cls):
        if hasattr(cls, "connections"):
            connections = getattr(cls, "connections")
            new_connections = connections.copy()
            return new_connections
        else:
            return dict()

    def to_record(self):
        result, data = dict(), self.__dict__
        for field, obj in data.items():
            if hasattr(obj, 'to_record'):
                value = obj.to_record()
                result[field] = value
            else:
                result[field] = obj
        return result

    def to_str(self):
        result, data = dict(), self.__dict__
        for field, obj in data.items():
            if hasattr(obj, 'to_str'):
                value = obj.to_record()
                result[field] = value
            elif isinstance(obj, datetime):
                result[field] = obj.strftime(constant.DATETIME_FORMAT)
            else:
                result[field] = obj
        return result

