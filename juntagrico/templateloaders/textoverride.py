"""
Wrapper for loading templates from the database.
"""

from django.template import Origin, TemplateDoesNotExist

from django.template.loaders.base import Loader as BaseLoader

from juntagrico.entity.textoverride import TextOverride


class Loader(BaseLoader):

    def get_contents(self, origin):
        try:
            text = TextOverride.objects.get(name__exact=origin.template_name)
        except TextOverride.DoesNotExist:
            raise TemplateDoesNotExist(origin)
        return text.text

    def get_template_sources(self, template_name, template_dirs=None):
        yield Origin(
            name=template_name,
            template_name=template_name,
            loader=self,
        )
