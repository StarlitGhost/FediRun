from ananas import PineappleBot, reply
from bs4 import BeautifulSoup
import requests

import zlib


class FediRun(PineappleBot):
    @reply
    def respond(self, status, user):
        username = user["acct"]

        soup = BeautifulSoup(status["content"], "lxml")
        [mention.extract() for mention in soup.find_all(class_="h-card")]
        [br.replace_with('\n') for br in soup.find_all("br")]
        lines = soup.text.splitlines()

        language = lines[0].strip()
        code = '\n'.join(lines[1:])

        returned, errors = self._tio(language, code)

        returned = [r.decode('utf-8', 'ignore') for r in returned]
        errors = [e.decode('utf-8', 'ignore') for e in errors]
        return_str = '\n'.join(returned)
        self._send_reply('{} {}'.format(username, return_str), status)

    def _tio(self, language, code, user_input=''):
        request = [{'command': 'V', 'payload': {'lang': [language]}},
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

        return returned, errors

    def _send_reply(self, response, original):
        self.mastodon.status_post(response,
                                  in_reply_to_id=original["id"],
                                  visibility=original["visibility"])
