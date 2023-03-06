from odoo import fields, models

from odoo.tools import float_round

import pytz
from datetime import datetime


def get_price_in_xof(currency_id, company_id, date):
    currency_name = currency_id.name
    if currency_name != 'XOF':
        rates = currency_id._get_rates(company_id, date)
        rate_value = 1
        if rates:
            for value in rates.values():
                rate_value = 1 / value
        return rate_value
    else:
        return 1


def get_xof_to_all_currency(currency):
    currency_name = currency.name
    if currency_name != 'XOF':
        cof = currency.rate_ids.company_rate

        return cof
    else:
        return 1


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    from_enc = fields.Boolean()
    amount_init = fields.Float(string='Montant taux initial')

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    def creation_rapport(self):
        tracking_obj = self.env['tracking.partner'].sudo()
        for val in self:
            if val.partner_type in ['supplier', 'customer']:
                action = {
                    'partner': val.partner_id.id,
                    'reference': val.name,
                    'designation': 'Paiement',
                    'libele_op': 'Paiement ' + val.name,
                    'date': val.date,
                    'payment_id': val.id,
                    'partner_type': val.partner_type,
                    'amount_currency': - val.amount
                }
                exist = tracking_obj.search([('payment_id', '=', val.id)])
                if val.partner_type == 'supplier':
                    action.update({'partner_type': 'vendor'})
                elif val.payment_type == 'customer':
                    action.update({'partner_type': 'customer'})
                if exist:
                    exist.write(action)
                else:
                    action.update({
                        'not_instance': True
                    })
                    if val.journal_id.type == 'bank':
                        action.update({'payment_method': 'bank'})
                    elif val.journal_id.type == 'cash':
                        action.update({'payment_method': 'espece'})
                    tracking_obj.sudo().create(action)

    def maj_tracking_partner_payment(self):
        if self.from_enc:
            print('Ecriture en cours')


    def action_post(self):
        res = super(AccountPayment, self).action_post()
        print('Paiement crée dans le suivi')
        self.creation_rapport()
        return res

    def action_draft(self):
        tracking_obj = self.env['tracking.partner'].sudo()
        for val in self:
            exist = tracking_obj.search([('payment_id', '=', val.id)])
            if exist:
                exist.unlink()
        return super(AccountPayment, self).action_draft()
