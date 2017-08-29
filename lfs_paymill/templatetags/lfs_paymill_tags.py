# django imports
from django import template
from django.conf import settings


register = template.Library()


class LFSPaymillJSNode(template.Node):
    def render(self, context):
        paymill_public_key = getattr(settings, "PAYMILL_PUBLIC_KEY", "")
        static_url = getattr(settings, "STATIC_URL", "")
        email = getattr(settings, "PAYMILL_EMAIL", "")

        return """
            <script type="text/javascript">
                var PAYMILL_PUBLIC_KEY = '%s';
                var PAYMILL_EMAIL = '%s';
            </script>
            <script type="text/javascript" src="https://bridge.paymill.com/"></script>
            <script type="text/javascript" src="%slfs_paymill/lfs_paymill_20170829.js"></script>
        """ % (paymill_public_key, email, static_url)


@register.tag
def lfs_paymill_js(parser, token):
    return LFSPaymillJSNode()
