import codecs
from collections import OrderedDict

from rest_framework.exceptions import ParseError
from rest_framework.parsers import BaseParser
from rest_framework.renderers import BaseRenderer


class UltraLight20Renderer(BaseRenderer):
    media_type = 'text/plain'
    format = 'ul2'
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            return ''

        items = ((name, ul20_format(value)) for (name, value) in data.items())
        text = '|'.join(k + '|' + v for (k, v) in items if v != '')
        return text.encode(self.charset)


def ul20_format(value):
    if value is None:
        return ''
    elif isinstance(value, bool):
        return '1' if value else '0'
    return str(value)


class UltraLight20Parser(BaseParser):
    media_type = 'text/plain'
    renderer_class = UltraLight20Renderer

    def parse(self, stream, media_type=None, parser_context=None):
        context = parser_context or {}
        encoding = context.get('encoding', 'utf-8')

        decoded_stream = codecs.getreader(encoding)(stream)
        data = decoded_stream.read()
        items = data.split('|')

        if len(items) % 2 != 0:
            raise ParseError('UL2.0 parse error: name/value pair mismatch')

        result = OrderedDict(items[i:(i + 2)] for i in range(0, len(items), 2))
        return result
