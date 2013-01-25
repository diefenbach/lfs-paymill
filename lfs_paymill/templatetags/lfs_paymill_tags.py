# django imports
from django import template
from django.conf import settings


register = template.Library()


class LFSPaymillJSNode(template.Node):
    def render(self, context):
        paymill_public_key = getattr(settings, "PAYMILL_PUBLIC_KEY", "")
        static_url = getattr(settings, "STATIC_URL", "")

        return """
            <script type="text/javascript" src="https://bridge.paymill.de/"></script>
            <script type="text/javascript" src="%slfs_paymill/lfs_paymill.js"></script>
            <script type="text/javascript">
                var PAYMILL_PUBLIC_KEY = '%s';
            </script>
        """ % (static_url, paymill_public_key)

@register.tag
def lfs_paymill_js(parser, token):
    return LFSPaymillJSNode()
