$(document).ready(function () {
    function PaymillResponseHandler(error, result) {
        if (error) {
            $(".payment-errors").text(error.apierror);
        } else {
            $(".payment-errors").text("");
            var form = $(".checkout-form");
            var token = result.token;
            form.append("<input type='hidden' name='paymillToken' value='" + token + "'/>");
            form.get(0).submit();
        }
        $(".button_order").removeAttr("disabled");
    }

    $(".checkout-form").submit(function (event) {
        if ($(".payment-method-type-2:checked").val() != null) {
            // Deactivate order button
            $('.button_order').attr("disabled", "disabled");

            if (false == paymill.validateCardNumber($('#id_credit_card_number').val())) {
                $(".payment-errors").text("Ungueltige Kartennummer");
                $(".button_order").removeAttr("disabled");
                return false;
            }

            if (false == paymill.validateExpiry($('#id_credit_card_expiration_date_month').val(), $('#id_credit_card_expiration_date_year').val())) {
                $(".payment-errors").text("Ungueltiges Gueltigkeitsdatum");
                $(".button_order").removeAttr("disabled");
                return false;
            }

            paymill.createToken({
                number:$('#id_credit_card_number').val(),
                exp_month:$('#id_credit_card_expiration_date_month').val(),
                exp_year:$('#id_credit_card_expiration_date_year').val(),
                cvc:$('#id_credit_card_verification').val(),
                cardholdername:$('#id_credit_card_owner').val(),
                amount:$('.amount').val(),
                currency:$('.currency').val()
            }, PaymillResponseHandler);

            return false;
        }
    });
});
