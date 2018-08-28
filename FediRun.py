from ananas import PineappleBot, reply
from bs4 import BeautifulSoup
import requests
from pyxdameraulevenshtein import normalized_damerau_levenshtein_distance as ndld

import zlib
from typing import List


class FediRun(PineappleBot):
    @reply
    def respond(self, status, user):
        username = user["acct"]

        soup = BeautifulSoup(status["content"], "lxml")
        [mention.extract() for mention in soup.find_all(class_="h-card")]
        [br.replace_with('\n') for br in soup.find_all("br")]
        lines = soup.text.splitlines()

        language = lines[0].strip()

        if not language:
            self._send_reply('@{} the language name *must* be on the first line of your toot'.format(username), status)
            return

        code = '\n'.join(lines[1:])

        returned, errors = self._tio(language, code)

        response = '@{} {}'.format(username, returned)
        if errors:
            response += '\nError: {}'.format(errors)

        self._send_reply(response, status)

    def _tio(self, language, code, user_input=''):
        if language.lower() in self.languages_friendly:
            language = self.languages_friendly[language.lower()]
        if language.lower() not in self.languages.keys():
            lang_list = self._closest_matches(language.lower(), self.languages.keys(), 10, 0.8)
            lang_string = "\n".join(lang_list)
            return ("", "language {!r} is unknown on tio.run.\n".format(language) +
                    "Perhaps you wanted one of these?\n\n" +
                    "{}".format(lang_string))

        request = [{'command': 'V', 'payload': {'lang': [language.lower()]}},
                   {'command': 'F', 'payload': {'.code.tio': code}},
                   {'command': 'F', 'payload': {'.input.tio': user_input}},
                   {'command': 'RC'}]
        req = b''
        for instr in request:
            req += instr['command'].encode()
            if 'payload' in instr:
                [(name, value)] = instr['payload'].items()
                req += b'%s\0' % name.encode()
                if type(value) == str:
                    value = value.encode()
                req += b'%u\0' % len(value)
                if type(value) != bytes:
                    value = '\0'.join(value).encode() + b'\0'
                req += value
        req_raw = zlib.compress(req, 9)[2:-4]

        url = "https://tio.run/cgi-bin/static/b666d85ff48692ae95f24a66f7612256-run/93d25ed21c8d2bb5917e6217ac439d61"
        res = requests.post(url, data=req_raw)
        res = zlib.decompress(res.content, 31)
        delim = res[:16]
        ret = res[16:].split(delim)
        count = len(ret) >> 1
        returned, errors = ret[:count], ret[count:]
        returned = [r.decode('utf-8', 'ignore') for r in returned]
        errors = [e.decode('utf-8', 'ignore') for e in errors]

        return_str = '\n'.join(returned)
        error_str = '\n'.join(errors)

        return return_str, error_str

    def start(self):
        self.languages = self._fetch_languages()
        self.languages_friendly = {d['name'].lower(): l for l, d in self.languages}

    def _fetch_languages(self):
        self.log("_fetch_languages", "Loading language list from TryItOnline...")
        lang_url = "https://raw.githubusercontent.com/TryItOnline/tryitonline/master/usr/share/tio.run/languages.json"
        response = requests.get(lang_url)
        return response.json()

    def _closest_matches(self, search: str, word_list: List[str], num_matches: int, threshold: float) -> List[str]:
        similarities = sorted([(ndld(search, word), word) for word in word_list])
        close_matches = [word for (diff, word) in similarities if diff <= threshold]
        top_n = close_matches[:num_matches]
        return top_n

    def _send_reply(self, response, original):
        self.mastodon.status_post(response,
                                  in_reply_to_id=original["id"],
                                  visibility=original["visibility"])
