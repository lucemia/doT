# https://github.com/olado/doT/blob/master/doT.js
# translate doT.js

import re

version = '1.0.0'
template_settings = {
                     "evaluate": r"\{\{([\s\S]+?\}?)\}\}",
                     "interpolate": r"\{\{=([\s\S]+?)\}\}",
                     "encode": r"\{\{!([\s\S]+?)\}\}",
                     "use":  r"\{\{#([\s\S]+?)\}\}",
                     "useParams": r"(^|[^\w$])def(?:\.|\[[\'\"])([\w$\.]+)(?:[\'\"]\])?\s*\:\s*([\w$\.]+|\"[^\"]+\"|\'[^\']+\'|\{[^\}]+\})",
                     "define": r"\{\{##\s*([\w\.$]+)\s*(\:|=)([\s\S]+?)#\}\}",
                     "defineParams": r"^\s*([\w$]+):([\s\S]+)",
                     "conditional": r"\{\{\?(\?)?\s*([\s\S]*?)\s*\}\}",
                     "iterate": r"\{\{~\s*(?:\}\}|([\s\S]+?)\s*\:\s*([\w$]+)\s*(?:\:\s*([\w$]+))?\s*\}\})",

                     "varname": "it",
                     "strip": True,
                     "append": True,
                     "selfcontained": False
                     }


startend = {
            "append": {
                       "start": "'+(",
                       "end": ")+'",
                       "endencode": "||'').toString().encodeHTML()+'"
                       },
            "split": {
                      "start": "';out+=(",
                      "end": ");out+='",
                      "endencode": "||'').toString().encodeHTML();out+='"
                      },
            }

skip = "$^"

def resolveDefs(c, tmpl, _def):
    # ignore the pre compile stage because we use it as backend translate.

    return tmpl

def unescape(code):
    return re.sub(r"[\r\t\n]", ' ', re.sub(r"\\('|\\)", "$1", code))

def template(tmpl, c = None, _def = None):
    c = c or template_settings
#    needhtmlencode = None
    sid = 0
#    indv = None

    cse = startend["append"] if c["append"] else startend["split"]

    def _interpolate(code):
        return cse["start"] + unescape(code) + cse["end"]

    def _encode(code):
        return cse['start'] + unescape(code) + cse["endencode"]

    def _conditional(elsecode, code):
        if elsecode:
            if code:
                return "';}else if(" + unescape(code) + "){out+='"
            else:
                return  "';}else{out+='"
        else:
            if code:
                return "';if(" + unescape(code) + "){out+='"
            else:
                return  "';}out+='"

    def _iterate(iterate, vname, iname, sid=sid):
        if (not iterate or not vname):
            return "';} } out+='"

        sid += 1
        indv = iname or "i" + str(sid)
        iterate = unescape(iterate)

        _sid = str(sid)
#        print iterate, vname, iname, _sid

        return "';var arr" + _sid + "=" + iterate + ";if(arr" + _sid + "){var " + vname + "," + indv + "=-1,l" + _sid + "=arr" + _sid + ".length-1;while(" + indv + "<l" + _sid + "){" + vname + "=arr" + _sid + "[" + indv + "+=1];out+='"

    def _evalute(code):
        return  "';" + unescape(code) + "out+='"

    _str = resolveDefs(c, tmpl, _def or {}) if(c["use"] or c["define"])  else tmpl


    if c.get('strip'):
        # remove white space
        _str = re.sub(r"(^|\r|\n)\t* +| +\t*(\r|\n|$)", " ", _str)
        _str = re.sub(r"\r|\n|\t|\/\*[\s\S]*?\*\/", '', _str)

    # _str = re.sub(r"|\\", '\\$&', _str)

    if c.get('interpolate'):
        _str = re.sub(c['interpolate'], lambda i:_interpolate(i.groups()[0]), _str)

    if c.get('encode'):
        _str = re.sub(c['encode'], lambda i: _encode(i.groups()[0]), _str)

    if c.get('conditional'):
        _str = re.sub(c['conditional'], lambda i: _conditional(i.groups()[0], i.groups()[1]), _str)

    if c.get('iterate'):
        _str = re.sub(c['iterate'], lambda i: _iterate(i.groups()[0], i.groups()[1], i.groups()[2]), _str)

    if c.get('evaluate'):
        _str = re.sub(c['evaluate'], lambda i: _evalute(i.groups()[0]), _str)


    # HINT:
    """.replace(/\n/g, '\\n').replace(/\t/g, '\\t').replace(/\r/g, '\\r')
            .replace(/(\s|;|\}|^|\{)out\+='';/g, '$1').replace(/\+''/g, '')
            .replace(/(\s|;|\}|^|\{)out\+=''\+/g,'$1out+=');

        if (needhtmlencode && c.selfcontained) {
            str = "String.prototype.encodeHTML=(" + encodeHTMLSource.toString() + "());" + str;
        }
        try {
            return new Function(c.varname, str);
        } catch (e) {
            if (typeof console !== 'undefined') console.log("Could not create a template function: " + str);
            throw e;
        }"""

    return "function anonymous(" + c["varname"] + ") {var out='" + _str + "';return out;}"


