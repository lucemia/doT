from .. import template, template_settings


def test_template(snapshot):
    template_settings["strip"] = False

    INPUT = r"{{?it.options == 1\n}}Option 1{{?? it.options == 2\n}}Option 2{{??\n}}Other option{{?}}:\n\n More text"
    assert snapshot == template(INPUT, template_settings)
