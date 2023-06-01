# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.tools import is_html_empty


class PaymentProviderInherit(models.Model):
    _inherit = 'payment.provider'

    _sql_constraints = [(
        'custom_providers_setup',
        "CHECK(custom_mode IS NULL OR (code = 'custom' AND custom_mode IS NOT NULL))",
        "Only custom providers should have a custom mode."
    )]

    custom_mode = fields.Selection(
        string="Custom Mode",
        selection_add=[('pay_in_cash', "Paiement en Espèces")],
        required_if_provider='custom',
    )

    @api.depends('code')
    def _compute_view_configuration_fields(self):
        """ Override of payment to hide the credentials page.

        :return: None
        """
        super(PaymentProviderInherit, self)._compute_view_configuration_fields()
        self.filtered(lambda p: p.code == 'custom').update({
            'show_credentials_page': False,
            'show_payment_icon_ids': False,
            'show_pre_msg': False,
            'show_done_msg': False,
            'show_cancel_msg': False,
        })

    def _transfer_ensure_pending_msg_is_set(self):
        super(PaymentProviderInherit, self)._transfer_ensure_pending_msg_is_set()
        transfer_providers_without_msg = self.filtered(
            lambda p: p.code == 'custom'
            and p.custom_mode == 'pay_in_cash'
            and is_html_empty(p.pending_msg)
        )

        if not transfer_providers_without_msg:
            return  # Don't bother translating the messages.

        account_payment_module = self.env['ir.module.module']._get('account_payment')
        if account_payment_module.state != 'installed':
            transfer_providers_without_msg.pending_msg = f'<div>' \
                f'<h3>{_("Paiement en Espèces à la Livraison")}</h3>' \
                f'<h4>{_("Communication")}</h4>' \
                f'<p>{_("Veuillez utiliser le nom de la commande comme référence de communication.")}</p>' \
                f'</div>'
            return

        for provider in transfer_providers_without_msg:
            company_id = provider.company_id.id
            accounts = self.env['account.journal'].search([
                ('type', '=', 'cash'), ('company_id', '=', company_id)
            ]).bank_account_id
            provider.pending_msg = f'<div>' \
                f'<h3>{_("Paiement en Espèces à la Livraison")}</h3>' \
                f'<h4>{_("Communication")}</h4>' \
                f'<p>{_("Veuillez utiliser le nom de la commande comme référence de communication.")}</p>' \
                f'</div>'

    def _get_removal_values(self):
        """ Override of `payment` to nullify the `custom_mode` field. """
        res = super(PaymentProviderInherit, self)._get_removal_values()
        res['custom_mode'] = None
        return res
