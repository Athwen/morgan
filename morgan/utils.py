from html.parser import HTMLParser
import re
from urllib.parse import urljoin

class IndexURLParser(HTMLParser):
    def __init__(self, base_url, *, convert_charrefs = True):
        super().__init__(convert_charrefs=convert_charrefs)
        self.base_url = base_url
        self.files = []
        self.is_href = False
        
        self.__create_file_json()
    
    def __create_file_json(self):
        json = {}

        json = {
            "core-metadata": False,
            "data-dist-info-metadata": False,
            "provenance": None,
            "requires-python": None,
            "size": None,
            "upload-time": None,
            "yanked": False,
            "hashes": {}
        }

        self.json = json

    def __get_hash_kv(self, hash_string):
        split = hash_string.split('=')

        return (split[0], split[1])

    def handle_starttag(self, tag, attrs):
        if (tag == 'a'):
            self.__create_file_json()
            self.is_href = True
            
            for attr in attrs:
                if (attr[0] == 'href'):
                    if ("#" in attr[1]):
                        kv = self.__get_hash_kv(attr[1].split('#')[1])
                        self.json['hashes'][kv[0]] = kv[1]

                    self.json['url'] = urljoin(self.base_url, attr[1])
                elif (attr[0] == 'data-dist-info-metadata'):
                    kv = self.__get_hash_kv(attr[1])

                    self.json['data-dist-info-metadata'] = {}
                    self.json['data-dist-info-metadata'][kv[0]] = kv[1]
                elif (attr[0] == 'data-core-metadata'):
                    kv = self.__get_hash_kv(attr[1])

                    self.json['core-metadata'] = {}
                    self.json['core-metadata'][kv[0]] = kv[1]
        else:
            self.is_href = False

    def handle_data(self, data):
        if (self.is_href):
            self.json['filename'] = data
        
            self.files.append(self.json)

def to_single_dash(filename):
    'https://packaging.python.org/en/latest/specifications/version-specifiers/#version-specifiers'

    # selenium-2.0-dev-9429.tar.gz
    m = re.search(r'-[0-9].*-', filename)
    if m:
        s2 = filename[m.start() + 1:]
        # 2.0-dev-9429.tar.gz
        s2 = s2.replace('-dev-', '.dev')
        # 2.0.dev9429.tar.gz
        s2 = s2.replace('-', '.')
        filename = filename[:m.start() + 1] + s2
    return filename
    # selenium-2.0.dev9429.tar.gz

def get_files(html, url_base):
    parser = IndexURLParser(url_base)
    parser.feed(html)

    return parser.files