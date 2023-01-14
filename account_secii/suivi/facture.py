from odoo import fields, models, api

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


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    change_partner_id = fields.Many2one('partner.charge', string='Change partner')
    change = fields.Boolean()

    @api.depends('company_id', 'invoice_filter_type_domain')
    def _compute_suitable_journal_ids(self):
        for m in self:
            journal_type = m.invoice_filter_type_domain or 'general'
            domain = []
            text = ()
            company_id = m.company_id.id or self.env.company.id
            if journal_type == "general":
                text = ('type', 'in', [journal_type, 'bank'])
                domain = [('company_id', '=', company_id), text]
            else:
                domain = [('company_id', '=', company_id), ('type', '=', journal_type)]
            m.suitable_journal_ids = self.env['account.journal'].search(domain)

    # creation de suivi
    def creation_rapport(self):
        tracking_obj = self.env['tracking.partner'].sudo()
        for val in self:
            if val.move_type in ['in_invoice', 'in_refund', 'out_invoice']:
                action = {
                    'partner': val.partner_id.id,
                    'reference': val.name,
                    'designation': 'Facture Achat',
                    'libele_op': 'Facture ' + val.name,
                    'date': self._default_time_utc(),
                    'move_id': val.id,

                }
                if val.move_type == 'in_refund':
                    action.update({
                        'designation': 'Avoir fournisseur',
                        'partner_type': 'vendor'
                    })
                elif val.move_type == 'in_invoice':
                    action.update(
                        {'partner_type': 'vendor'}
                    )
                elif val.move_type == 'out_invoice':
                    action.update(
                        {'partner_type': 'customer',
                         'designation': 'Facture Vente'}
                    )
                exist = tracking_obj.search([('move_id', '=', val.id)])
                if exist:
                    if val.currency_id.name == 'XOF':
                        action.update({
                            'amount_currency': str('{:,}'.format(float_round(- val.amount_total, 0)).replace(',',
                                                                                                             ' ')) + ' ' + val.currency_id.symbol,
                            # 'amount_cf': val.amount_total,

                        })
                        exist.write(action)
                else:
                    if val.currency_id.name == 'XOF':
                        action.update({
                            'amount_currency': str('{:,}'.format(float_round(- val.amount_total, 0)).replace(',',
                                                                                                             ' ')) + ' ' + val.currency_id.symbol,
                            # 'amount_cf': val.amount_total,
                            'move_id': val.id,
                            'not_instance': True

                        })
                        tracking_obj.create(action)

    def recup_facture(self):
        check = self.env['account.move'].sudo().search([('state', '=', 'posted')])
        print('Longueur', len(check))
        for elt in check:
            if elt.move_type in ['in_invoice', 'in_refund', 'out_invoice']:
                action = {
                    'partner': elt.partner_id.id,
                    'reference': elt.name,
                    'designation': 'Facture Achat',
                    'libele_op': 'Facture ' + elt.name,
                    'date': elt.create_date,
                    'move_id': elt.id,
                }
                if elt.move_type == 'in_refund':
                    action.update({
                        'designation': 'Avoir fournisseur',
                        'partner_type': 'vendor'
                    })
                elif elt.move_type == 'in_invoice':
                    action.update(
                        {'partner_type': 'vendor'}
                    )
                elif elt.move_type == 'out_invoice':
                    action.update(
                        {'partner_type': 'customer',
                         'designation': 'Facture Vente'}
                    )
                tracking = self.env['tracking.partner'].sudo().search([('move_id', '=', elt.id)])
                if tracking:
                    action.update({
                        'amount_currency': elt.amount_total
                    })
                    tracking.sudo().write(action)
                else:
                    action.update({
                        'amount_currency': elt.amount_total,
                        'move_id': elt.id,
                        'not_instance': True
                    })
                    tracking.sudo().create(action)

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if not self.change:
            self.creation_rapport()
        move_line = self.env['account.move.line'].search([('move_id', '=', self.id)])
        for line in move_line:
            if not line.payment_id and not line.move_id.change_partner_id:
                amount = str(self.amount_total).replace('.0', '')
                text = ' '
                if line.move_id.move_type == 'in_invoice':
                    text = 'Facture fournisseur '
                elif line.move_id.move_type == 'out_invoice':
                    text = 'Facture client '
                if self.currency_id.name == 'XOF' and self.partner_id:
                    line.name = text + amount + ' ' + self.currency_id.symbol + ' - ' \
                                + self.partner_id.name + ' - ' + self.invoice_date.strftime("%d/%m/%Y")
        return res

    def button_draft(self):
        tracking_obj = self.env['tracking.partner'].sudo()
        for val in self:
            exist = tracking_obj.search([('move_id', '=', val.id)])
            if exist:
                exist.unlink()
        return super(AccountMove, self).button_draft()


class InheritAccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    is_use = fields.Boolean(string='deja utilise', compute='add_change_to_tracking', store = True,
                            help='Permet de dire si un une change a ete ajoute dans le suivi '
                                 'fournisseur ou pas')

    @api.depends('account_id', 'name', 'debit', 'credit')
    def add_change_to_tracking(self):
        trackings = self.env['account.move.line'].search([('account_id.code', 'in', ('776000', '676000'))])
        for val in trackings:
            if not val.is_use and not val.move_id.change:
                action = {
                    'partner': val.partner_id.id,
                    'reference': val.name,
                    'designation': 'Change',
                    'libele_op': val.name,
                    'date': val.date,
                    'payment_ref': str(val.id) + 'CHANG',
                    'partner_type': 'vendor',
                    'not_instance': True

                }
                # gain
                if val.account_id.code == str(776000):
                    action.update({
                        # 'credit': val.credit,
                        'amount_currency': str(val.amount_currency) + ' CFA',
                        # 'amount_cf': val.credit,

                    })
                # perte
                elif val.account_id.code == str(676000):
                    action.update({
                        # 'debit': val.debit,
                        'amount_currency': str(val.amount_currency) + ' CFA',
                        # 'amount_cf': - val.debit,

                    })
                self.env['tracking.partner'].sudo().create(action)
            val.is_use = True
            val.move_id.change = True
