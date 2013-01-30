# python imports
import locale

# django imports
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# pycurl imports
import requests

# lfs imports
import lfs.cart.utils
import lfs.customer.utils
import lfs.payment.utils
import lfs.shipping.utils
from lfs.order.settings import PAID
from lfs.plugins import PaymentMethodProcessor
from lfs.plugins import PM_ORDER_ACCEPTED
from lfs.voucher.models import Voucher


MESSAGES = {
    10001: _(u"General undefined response."),
    10002: _(u"Still waiting on something."),
    40000: _(u"General problem with data."),
    40100: _(u"Problem with creditcard data."),
    40101: _(u"Problem with cvv."),
    40102: _(u"Card expired or not yet valid."),
    40103: _(u"Limit exceeded."),
    40200: _(u"Problem with bank account data."),
    40300: _(u"Problem with 3d secure data."),
    50000: _(u"General problem with backend."),
    50100: _(u"Technical error with credit card."),
    50101: _(u"Error limit exceeded."),
    50200: _(u"Technical error with bank account."),
    50300: _(u"Technical error with 3D secure."),
    50400: _(u"Decline because of risk issues."),
}


class PaymillPaymentMethodProcessor(PaymentMethodProcessor):
    """
    Provides payment processment with paymill.com.
    """
    def process(self):
        """
        Processes the payment.
        """
        try:
            amount = int("%.0f" % (self._calculate_price() * 100))
            cart_id = self.cart.id
            currency = locale.localeconv().get("int_curr_symbol").strip()
            customer = lfs.customer.utils.get_customer(self.request)
        except:
            return {
                "accepted": False,
                "message": _(u"An error with the credit card occured, please try again later or use a other payment method."),
                "message_location": "credit_card",
            }

        # For any reason python-format isn't working here.
        description = _(u"Credit cart payment for customer") + u": %s" % customer.id
        description = description.encode("utf-8")

        payload = {
            "token": self.request.POST.get("paymillToken", ""),
            "currency": currency,
            "amount": amount,
            "description": description,
        }

        result = requests.post(
            "https://api.paymill.com/v2/transactions",
            auth = (getattr(settings, "PAYMILL_PRIVATE_KEY"), ""),
            params = payload,
        )

        result = result.json()
        response_code = result.get("data", {}).get("response_code", 0)

        if response_code == 20000:
            return {
                "accepted": True,
                "order_state": PAID,
            }
        else:
            message = MESSAGES.get(response_code, _(u"An error with the credit card occured, please try again later or use a other payment method."))

            return {
                "accepted": False,
                "message": message,
                "message_location": "credit_card",
            }

    def get_create_order_time(self):
        return PM_ORDER_ACCEPTED


    def _calculate_price(self):
        """
        Calculates the total price of the current order.
        """
        shipping_method = lfs.shipping.utils.get_selected_shipping_method(self.request)
        shipping_costs = lfs.shipping.utils.get_shipping_costs(self.request, shipping_method)

        payment_method = lfs.payment.utils.get_selected_payment_method(self.request)
        payment_costs = lfs.payment.utils.get_payment_costs(self.request, payment_method)

        # Calculate the totals
        price = self.cart.get_price_gross(self.request) + shipping_costs["price"] + payment_costs["price"]

        # Discounts
        discounts = lfs.discounts.utils.get_valid_discounts(self.request)
        for discount in discounts:
            price = price - discount["price_gross"]

        # Add voucher if one exists
        try:
            voucher_number = lfs.voucher.utils.get_current_voucher_number(self.request)
            voucher = Voucher.objects.get(number=voucher_number)
        except Voucher.DoesNotExist:
            voucher = None
        else:
            is_voucher_effective, voucher_message = voucher.is_effective(self.request, self.cart)
            if is_voucher_effective:
                voucher_price = voucher.get_price_gross(self.request, self.cart)
                price -= voucher_price

        return price
