from .. import template_settings, template

def test_template(snapshot):
    setting = template_settings._replace(strip = False)

    INPUT = r"{{?it.options == 1\n}}Option 1{{?? it.options == 2\n}}Option 2{{??\n}}Other option{{?}}:\n\n More text"
    assert snapshot == template(INPUT, setting)