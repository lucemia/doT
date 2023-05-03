# https://github.com/olado/doT/blob/master/doT.js
# translate doT.js

from code import interact
import re
import operator
from typing import NamedTuple

version = "1.1.1"

class TemplateSettings(NamedTuple):
    evaluate: str = r"\{\{([\s\S]+?(\}?)+)\}\}"
    interpolate: str = r"\{\{=([\s\S]+?)\}\}"
    encode: str = r"\{\{!([\s\S]+?)\}\}"
    use: str = r"\{\{#([\s\S]+?)\}\}"
    useParams:str = r"(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"[^\"]+\"|\'[^\']+\'|\{[^\}]+\})",
    define: str = r"\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}"
    defineParams: str = r"^\s*([\w$]+):([\s\S]+)"
    conditional: str = r"\{\{\?(\?)?\s*([\s\S]*?)\s*\}\}"
    iterate: str = r"\{\{~\s*(?:\}\}|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\}\})"
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
    split: Symbol = Symbol(start="';out+=(", end=");out+='", startencode="';out+=encodeHTML(")


startend: StartEnd = StartEnd()

skip: str = "$^"


def resolveDefs(c, tmpl, _def):
    # ignore the pre compile stage because we use it as backend translate.

    return tmpl


def unescape(code: str) -> str:
    return re.sub(r"\\('|\\)", r"\1", re.sub(r"[\r\t\n]", " ", code))



def template(tmpl, c: TemplateSettings=None, _def=None):
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
            return "';}else if(" + unescape(code) + "){out+='" if code else "';}else{out+='"
        else:
            return "';if(" + unescape(code) + "){out+='" if code else "';}out+='"

    def iterate_func(m, iterate, vname, iname):
        nonlocal sid
        if not iterate: 
            return "';} } out+='"
        sid += 1
        indv = iname or "i"+_str(sid)
        iterate = unescape(iterate)
        return "';var arr"+_str(sid)+"="+iterate+";if(arr"+_str(sid)+"){var "+vname+","+indv+"=-1,l"+_str(sid)+"=arr"+_str(sid)+".length-1;while("+indv+"<l"+_str(sid)+"){"            +vname+"=arr"+_str(sid)+"["+indv+"+=1];out+='"

    def evaluate_func(m, code):
        return "';" + unescape(code) + "out+='"

    if 'strip' in c and c.strip:
        _str = re.sub(r"(^|\r|\n)\t* +| +\t*(\r|\n|$)", " ", _str)
        _str = re.sub(r"\r|\n|\t|\/\*[\s\S]*?\*\/", "", _str)

    _str = "var out='" + _str
    _str = re.sub(r"'|\\", r"\\$&", _str)
    _str = re.sub(c.interpolate if 'interpolate' in c else skip, interpolate_func, _str)
    _str = re.sub(c.encode if 'encode' in c else skip, encode_func, _str)
    _str = re.sub(c.conditional if 'conditional' in c else skip, conditional_func, _str)
    _str = re.sub(c.iterate if 'iterate' in c else skip, iterate_func, _str)
    _str = re.sub(c.evaluate if 'evaluate' in c else skip, evaluate_func, _str)
    _str += "';return out;"
    _str = re.sub(r"\n", "\\n", _str)
    _str = re.sub(r"\t", "\\t", _str)
    _str = re.sub(r"\r", "\\r", _str)
    _str = re.sub(r"(\s|;|\}|^|\{)out\+='';", r'\1', _str)
    _str = re.sub(r"\+''", "", _str)

    return (
        "function anonymous(" + c.varname + ") {var out='" + _str + "';return out;}"
    )
