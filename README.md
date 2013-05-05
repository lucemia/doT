doT.py
======

A python implementation of the famous js template engine. doT.js. http://olado.github.io/doT/index.html.
It do excetly the same thing as doT.js except can be run in Server side without Node.js

doT.py compile the template in server to a pure javascript function, therefore it can later be evalute in client side without any dependecny. It allows using client side template tech without template engine.
to mininal the depenance and loading for client side.

Which means it saves the time for client
1) wait the template engine loading.
2) wait the template loading.

Here is an example:

With client side template engine to load ajax data.

```html
<html>
<script type="text/javascript" src="[path_to_template_engine]"></script>
<div id=""
<script>

</script>

</html>
```

With doT.py, you write:
```html

<script type="text/javascript">
    var fn = {{ js_template("123.html") }};
    var body.innerHtml = fn(data);
</script>

```
it compiled to

```html
<script type="text/javascript">
    var fn = {{ js_template("123.html") }};
    var body.innerHtml = fn(data);
</script>
```

Django Support:

Jinja2 Support:

Commandline Support:
