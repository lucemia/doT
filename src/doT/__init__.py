# https://github.com/olado/doT/blob/master/doT.js
# translate doT.js

import re
from typing import NamedTuple

version = "1.1.1"


class TemplateSettings(NamedTuple):
    evaluate: str = r"\{\{([\s\S]+?(\}?)+)\}\}"
    interpolate: str = r"\{\{=([\s\S]+?)\}\}"
    encode: str = r"\{\{!([\s\S]+?)\}\}"
    use: str = r"\{\{#([\s\S]+?)\}\}"
    useParams: str = (
        r"(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"[^\"]+\"|\'[^\']+\'|\{[^\}]+\})",
    )
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


class Symbol(NamedTuple):
    start: str
    end: str
    startencode: str


class StartEnd(NamedTuple):
    append: Symbol = Symbol(start="'+(", end=")+'", startencode="'+encodeHTML(")
    split: Symbol = Symbol(
        start="';out+=(", end=");out+='", startencode="';out+=encodeHTML("
    )


startend: StartEnd = StartEnd()

skip: str = "$^"


import re


def resolve_defs(c, block, def_dict):
    def skip(match):
        return ""

    if isinstance(block, str):
        block_str = block
    else:
        block_str = block.__str__()

    # Replace c.define
    define = c.get("define", skip)

    def replacement(match):
        code, assign, value = match.groups()
        if code.startswith("def."):
            code = code[4:]

        if code not in def_dict:
            if assign == ":":
                if c.get("defineParams", None):

                    def sub_replacement(m):
                        param, v = m.groups()
                        def_dict[code] = {"arg": param, "text": v}
                        return ""

                    pattern = re.compile(c["defineParams"])
                    value = pattern.sub(sub_replacement, value)

                if code not in def_dict:
                    def_dict[code] = value
            else:
                exec(f"def_dict['{code}'] = {value}", {"def": def_dict})

        return ""

    pattern = re.compile(define)
    block_str = pattern.sub(replacement, block_str)

    # Replace c.use
    use = c.get("use", skip)

    def replacement(match):
        code = match.group(1)

        if c.get("useParams", None):

            def sub_replacement(m):
                s, d, param = m.groups()
                if d in def_dict and "arg" in def_dict[d] and param:
                    rw = (d + ":" + param).replace("'", "_").replace("\\", "_")
                    def_dict["__exp"] = def_dict.get("__exp", {})
                    def_dict["__exp"][rw] = re.sub(
                        r"(^|[^\\w$])" + re.escape(def_dict[d]["arg"]) + r"([^\\w$])",
                        r"\1" + param + r"\2",
                        def_dict[d]["text"],
                    )
                    return s + f"def.__exp['{rw}']"

            pattern = re.compile(c["useParams"])
            code = pattern.sub(sub_replacement, code)

        def_dict_eval = eval(code, {"def": def_dict})
        return (
            resolve_defs(c, def_dict_eval, def_dict) if def_dict_eval else def_dict_eval
        )

    pattern = re.compile(use)
    block_str = pattern.sub(replacement, block_str)

    return block_str


def unescape(code: str) -> str:
    return re.sub(r"\\('|\\)", r"\1", re.sub(r"[\r\t\n]", " ", code))


def template(tmpl, c: TemplateSettings = None, _def=None):
    c = c or template_settings
    cse = startend.append if c.append else startend.split
    needhtmlencode = None
    sid = 0
    indv = None

    _str = resolveDefs(c, tmpl, _def) if c.use or c.define else tmpl

    def interpolate_func(m, code):
        return cse.start + unescape(code) + cse.end

    def encode_func(m, code):
        needhtmlencode = True
        return cse.startencode + unescape(code) + cse.end

    def conditional_func(m, elsecase, code):
        if elsecase:
            return (
                "';}else if(" + unescape(code) + "){out+='"
                if code
                else "';}else{out+='"
            )
        else:
            return "';if(" + unescape(code) + "){out+='" if code else "';}out+='"

    def iterate_func(m, iterate, vname, iname):
        nonlocal sid
        if not iterate:
            return "';} } out+='"
        sid += 1
        indv = iname or "i" + _str(sid)
        iterate = unescape(iterate)
        return (
            "';var arr"
            + _str(sid)
            + "="
            + iterate
            + ";if(arr"
            + _str(sid)
            + "){var "
            + vname
            + ","
            + indv
            + "=-1,l"
            + _str(sid)
            + "=arr"
            + _str(sid)
            + ".length-1;while("
            + indv
            + "<l"
            + _str(sid)
            + "){"
            + vname
            + "=arr"
            + _str(sid)
            + "["
            + indv
            + "+=1];out+='"
        )

    def evaluate_func(m, code):
        return "';" + unescape(code) + "out+='"

    if "strip" in c and c.strip:
        _str = re.sub(r"(^|\r|\n)\t* +| +\t*(\r|\n|$)", " ", _str)
        _str = re.sub(r"\r|\n|\t|\/\*[\s\S]*?\*\/", "", _str)

    _str = "var out='" + _str
    _str = re.sub(r"'|\\", r"\\$&", _str)
    _str = re.sub(c.interpolate if "interpolate" in c else skip, interpolate_func, _str)
    _str = re.sub(c.encode if "encode" in c else skip, encode_func, _str)
    _str = re.sub(c.conditional if "conditional" in c else skip, conditional_func, _str)
    _str = re.sub(c.iterate if "iterate" in c else skip, iterate_func, _str)
    _str = re.sub(c.evaluate if "evaluate" in c else skip, evaluate_func, _str)
    _str += "';return out;"
    _str = re.sub(r"\n", "\\n", _str)
    _str = re.sub(r"\t", "\\t", _str)
    _str = re.sub(r"\r", "\\r", _str)
    _str = re.sub(r"(\s|;|\}|^|\{)out\+='';", r"\1", _str)
    _str = re.sub(r"\+''", "", _str)

    return "function anonymous(" + c.varname + ") {var out='" + _str + "';return out;}"
