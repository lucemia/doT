doT.py
======

A python implementation of the famous js template engine. doT.js. http://olado.github.io/doT/index.html.
It do excetly the same thing as doT.js except written in python. Thus, it can be used in python web framework.

doT.py compile the template to a pure javascript function in server side; therefore client side can evaluate the template later without any dependency. Which means it saves the time for client to load template engine and to load template file. In short, doT.py allows using client side template tech without include a template engine in client side.

## Installation

`pip install doT-js-py`

### Here is an example:

#### Use client side template

```html
<html>
<!-- load template engine -->
<script type="text/javascript" src="doT.js"></script>
<div id="container">
<script type="text/javascript">
     // Compile template function
     var tempFn = doT.template("<h1>Here is a sample template {{=it.foo}}</h1>");
     var resultText = tempFn({foo: 'with doT'});
     document.getElementById('container').innerHtml = resultText;
</script>
</html>
```

#### Use doT.py, you write:
```html
<html>
<!-- without loading template engine -->
<div id="container">
<script type="text/javascript">
     // Compile template function
     var tempFn = {{ js_template('<h1>Here is a sample template {{=it.foo}}</h1>') }};
     var resultText = tempFn({foo: 'with doT'});
     document.getElementById('container').innerHtml = resultText;
</script>
</html>
```

#### it will automatically compiled to
```html
<html>
<!-- without loading template engine -->
<div id="container">
<script type="text/javascript">
     // Compile template function
     var tempFn = function anonymous(it) { var out='"<h1>Here is a sample template '+(it.foo)+'</h1>"';return out; };
     var resultText = tempFn({foo: 'with doT'});
     document.getElementById('container').innerHtml = resultText;
</script>
</html>
```

Django Support:

Jinja2 Support:

Commandline Support:
