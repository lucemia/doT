# https://github.com/olado/doT/blob/master/doT.js
# translate doT.js

import re
from typing import Callable, NamedTuple, Union

version = "1.1.1"


class TemplateSettings(NamedTuple):
    evaluate: str = r"\{\{([\s\S]+?\}?)\}\}"
    interpolate: str = r"\{\{=([\s\S]+?)\}\}"
    encode: str = r"\{\{!([\s\S]+?)\}\}"
    use: str = r"\{\{#([\s\S]+?)\}\}"
    useParams: str = r"(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"[^\"]+\"|\'[^\']+\'|\{[^\}]+\})"
    define: str = r"\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}"
    defineParams: str = r"^\s*([\w$]+):([\s\S]+)"
    conditional: str = r"\{\{\?(\?)?\s*([\s\S]*?)\s*\}\}"
    iterate: str = (
        r"\{\{~\s*(?:\}\}|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\}\})"
    )
    varname: str = "it"
    strip: bool = True
    append: bool = True
    selfcontained: bool = False
    doNotSkipEncoded: bool = False


template_settings: TemplateSettings = TemplateSettings()


def replace(
    original_str: str, pattern: str, repl_func: Union[Callable[[re.Match], str], str]
) -> str:
    return re.sub(pattern, repl_func, original_str)


def encodeHTMLsource(do_not_skip_encoded: bool) -> Callable[[str], str]:
    encode_HTML_rules = {
        "&": "&#38;",
        "<": "&#60;",
        ">": "&#62;",
        '"': "&#34;",
        "'": "&#39;",
        "/": "&#47;",
    }
    match_HTML = (
        re.compile(r'[&<>"\'\/]')
        if do_not_skip_encoded
        else re.compile(r'&(?!#?\w+;)|<|>|"|\'|\/')
    )

    def encode(code: str) -> str:
        return (
            match_HTML.sub(
                lambda m: encode_HTML_rules.get(m.group(0), m.group(0)), str(code)
            )
            if code
            else ""
        )

    return encode


class Symbol(NamedTuple):
    start: str
    end: str
    startencode: str


class StartEnd(NamedTuple):
    append: Symbol = Symbol(start="'+(", end=")+'", startencode="'+encodeHTML(")
    split: Symbol = Symbol(
        start="';out+=(",
        end=");out+='",
        startencode="';out+=encodeHTML(",
    )


startend: StartEnd = StartEnd()

skip = r"$^"


def resolveDefs(c, tmpl: str, _def) -> str:
    # ignore the pre compile stage because we use it as backend translate.

    return tmpl


def unescape(code: str) -> str:
    code = re.sub(r"\\('|\\)", r"\1", code)
    code = re.sub(r"[\r\t\n]", " ", code)
    return code


def template(tmpl: str, c: TemplateSettings = None, _def=None):
    c = c or template_settings
    cse = startend.append if c.append else startend.split
    needhtmlencode = None
    sid = 0
    indv = None

    _str = resolveDefs(c, tmpl, _def or {}) if (c.use or c.define) else tmpl
    # print(f"resolveDefs: {_str}")

    if c.strip:
        # remove white space
        _str = re.sub(r"(^|\r|\n)\t* +| +\t*(\r|\n|$)", " ", _str)
        _str = re.sub(r"\r|\n|\t|\/\*[\s\S]*?\*\/", "", _str)

    # print(f"strip: {_str}")
    _str = replace(_str, r"['\\]", r"\\\g<0>")

    # print(f"replace: {_str}")

    def _interpolate(match: re.Match) -> str:
        code = match.groups()[0]
        return cse.start + unescape(code) + cse.end

    _str = replace(_str, c.interpolate or skip, _interpolate)
    # print(f"interpolate: {_str}")

    def _encode(match: re.Match) -> str:
        nonlocal needhtmlencode
        needhtmlencode = True
        code = match.groups()[0]
        return cse.start + unescape(code) + cse.end

    _str = replace(_str, c.encode or skip, _encode)
    # print(f"encode: {_str}")

    def _conditional(match: re.Match) -> str:
        elsecode = match.groups()[0]
        code = match.groups()[1]

        if elsecode:
            if code:
                return "';}else if(" + unescape(code) + "){out+='"
            else:
                return "';}else{out+='"
        else:
            if code:
                return "';if(" + unescape(code) + "){out+='"
            else:
                return "';}out+='"

    _str = replace(_str, c.conditional or skip, _conditional)
    # print(f"conditional: {_str}")

    def _iterate(match: re.Match) -> str:
        iterate = match.groups()[0]
        vname = match.groups()[1]
        iname = match.groups()[2]
        nonlocal sid, indv

        if not iterate:
            return "';} } out+='"

        sid += 1
        indv = iname or "i" + str(sid)
        iterate = unescape(iterate)

        _sid = str(sid)
        return (
            "';var arr"
            + _sid
            + "="
            + iterate
            + ";if(arr"
            + _sid
            + "){var "
            + vname
            + ","
            + indv
            + "=-1,l"
            + _sid
            + "=arr"
            + _sid
            + ".length-1;while("
            + indv
            + "<l"
            + _sid
            + "){"
            + vname
            + "=arr"
            + _sid
            + "["
            + indv
            + "+=1];out+='"
        )

    _str = replace(_str, c.iterate or skip, _iterate)
    # print(f"iterate: {_str}")

    def _evalute(match: re.Match) -> str:
        code = match.groups()[0]
        return "';" + unescape(code) + "out+='"

    _str = replace(_str, c.evaluate or skip, _evalute)
    # print(f"evaluate: {_str}")

    _str = replace(_str, r"\n", "\\n")
    _str = replace(_str, r"\t", "\\t")
    _str = replace(_str, r"\r", "\\r")
    _str = replace(_str, r"(\s|;|\}|^|\{)out\+='';", r"\1")
    _str = replace(_str, r"\+''", "")

    # print(f"final: {_str}")
    # if (needhtmlencode):
    #     if (c.selfcontained or c.doNotSkipEncoded):

    return "function anonymous(" + c.varname + ") {var out='" + _str + "';return out;}"
