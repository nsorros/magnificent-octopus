import esprit
from esprit import mappings
from octopus.core import app
import json as jsonlib

class ESDAO(esprit.dao.DomainObject):
    __type__ = 'index'
    __conn__ = esprit.raw.Connection(app.config.get('ELASTIC_SEARCH_HOST'), app.config.get('ELASTIC_SEARCH_INDEX'))

    @classmethod
    def mappings(cls):
        return {
            cls.__type__ : mappings.for_type(
                cls.__type__,
                    mappings.properties(mappings.type_mapping("location", "geo_point")),
                    mappings.dynamic_templates(
                    [
                        mappings.EXACT,
                    ]
                )
            )
        }

    def json(self):
        return jsonlib.dumps(self.data)

    def prep(self):
        pass

    def save(self, **kwargs):
        self.prep()
        super(ESDAO, self).save(**kwargs)
