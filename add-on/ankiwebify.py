# This code is use to change markdown README to HTML in the AnkiWeb page
# This is not written by me. Thanks for user "abdo"
# Reference: https://forums.ankiweb.net/t/markdown-to-addon-description-conversion/17768

import sys
import re

from markdown import markdown
from bs4 import BeautifulSoup

allowed_tags = ["img", "a", "b", "i", "code", "ul", "ol", "li", "div"]


def ankiwebify(filename):
    with open(filename, "r", encoding="utf-8") as f:
        html = markdown(f.read(), output_format="html5")
    doc = BeautifulSoup(html, "html.parser")

    # add the "markdown" attribute so that markdown inside html tags in the original text is parsed
    for node in doc():
        node["markdown"] = "1"

    # reparse markdown again
    html = markdown(doc.decode(False), output_format="html5", extensions=["md_in_html"])

    # strip markdown attribute
    html = html.replace(' markdown="1"', "")

    # convert headings to <b> elements
    html = re.sub(
        r"<h(?P<num>\d+)>(.*?)</h(?P=num)>",
        lambda m: "\n<b>" + m.group(2) + f"</b>",
        html,
    )

    # collapse newlines inside paragraphs
    # TODO: do the same for lists?
    html = re.sub(
        r"(<p.*?>)(.*?)(</p.*?>)",
        lambda m: m.group(1) + m.group(2).replace("\n", "\xA0") + m.group(3),
        html,
        flags=re.DOTALL,
    )

    html = re.sub("\n\\s+", "\xA0", html)

    # convert <br>'s to newlines
    html = re.sub(r"(<br>)|(</br>)", "\n", html)

    # remove disallowed tags
    def remove_disallowed_tag(m):
        tag = m.group(2)
        if tag in allowed_tags:
            return m.group(0)
        else:
            return ""

    html = re.sub(r"(<([^/>\s]+).*?>)", remove_disallowed_tag, html, flags=re.DOTALL)
    html = re.sub(r"(</([^>\s]+).*?>)", remove_disallowed_tag, html, flags=re.DOTALL)

    return html


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("no input file given", file=sys.stderr)
        sys.exit(1)
    print(ankiwebify(sys.argv[1]))
