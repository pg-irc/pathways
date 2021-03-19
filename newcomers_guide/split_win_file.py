import re


def is_chapter(line):
    regex = r'[\d ]*CHAPTER.*'
    if re.fullmatch(regex, line):
        return True
    return False


def get_chapter(line):
    regex = r'[\d ]*(CHAPTER.*)'
    result = re.match(regex, line)[1].strip()
    if len(result) < len('CHAPTER 8 - '):
        raise RuntimeError(line)
    return result


def is_title(line):
    regex = r'[\d\. ]*Topic:.*'
    if re.fullmatch(regex, line):
        return True
    return False


def get_title(line):
    regex = r'[\d\. ]*Topic:(.*)'
    result = re.match(regex, line)[1].strip()
    if result == '':
        raise RuntimeError(line)
    return result


def is_tag(line):
    regex = r'Tags:.*'
    if re.fullmatch(regex, line):
        return True
    return False


def get_tags(line):
    regex = r'Tags:(.*)'
    result = re.match(regex, line)[1].strip().split()
    return result


class Topic:
    def __init__(self, chapter, topic, tags, text):
        self.chapter = chapter
        self.topic = topic
        self.tags = tags
        self.text = text

    def validate(self):
        if self.chapter == '':
            raise RuntimeError(f'{self.topic}: Chapter is empty')
        if self.chapter.find('/') != -1:
            raise RuntimeError(f'{self.chapter}: Chapter topic contains invalid / character')
        if self.topic.find('/') != -1:
            raise RuntimeError(f'{self.topic}: Topic topic contains invalid / character')

    def file_path(self, root=''):
        self.validate()
        return f'{self.clean_root(root)}mb/{self.chapter}/topics/{self.topic}/'

    def file_name(self, root='', locale='en'):
        self.validate()
        return f'{self.clean_root(root)}mb/{self.chapter}/topics/{self.topic}/{locale}.{self.topic}.md'

    def taxonomy_file_name(self, root=''):
        self.validate()
        return f'{self.clean_root(root)}mb/{self.chapter}/topics/{self.topic}/taxonomy.txt'

    def clean_root(self, root):
        if root == '' or root.endswith('/'):
            return root
        return root + '/'

    def tags_for_writing(self):
        return ', '.join(self.tags)


class WinFileParser:
    def __init__(self):
        self.topics = []
        self.chapter = ''
        self.clear()

    def clear(self):
        self.topic = ''
        self.tags = []
        self.text = ''

    def parse(self, stream, line):
        if is_chapter(line):
            self.save_current_topic()
            self.chapter = get_chapter(line)
        elif is_title(line):
            self.save_current_topic()
            self.topic = get_title(line)
        elif is_tag(line):
            self.tags = get_tags(line)
        else:
            self.text += line + '\n'

    def save_current_topic(self):
        if self.topic:
            self.topics.append(Topic(self.chapter, self.topic, self.tags, self.text))
        self.clear()

    def done(self):
        self.save_current_topic()
        return self


def parse_string(text):
    parser = WinFileParser()
    for line in text.split('\n'):
        parser.parse(None, line)
    return parser.done()


def parse_file(stream, path):
    parser = WinFileParser()
    with open(path, 'r') as fp:
        line = fp.readline()
        while line:
            parser.parse(stream, line.strip())
            line = fp.readline()
    return parser.done()
