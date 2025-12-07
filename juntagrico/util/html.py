from html.parser import HTMLParser


class EmailHtmlParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.text = ''
        self.url = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.url = value
        if tag == "br":
            self.text += '\n'

    def handle_data(self, data):
        self.text += data

    def handle_endtag(self, tag):
        # add url at the end of the link
        if tag == "a":
            if self.url:
                if not self.text.endswith(self.url):  # ignore if link text is link url
                    self.text += f' ( {self.url} )'
                self.url = None
        if tag == "p":
            self.text += '\n\n'
