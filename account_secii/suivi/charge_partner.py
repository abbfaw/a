# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

import pytz
from odoo.tools import float_round


class partnerCharge(models.Model):
    _name = "partner.charge"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin']
    _rec_name = "partner"
    _order = 'create_date desc'

    def _filter_default_purchases(self):
        all_purchases = self.env['purchase.order'].search([('is_prive', '=', True)])
        return all_purchases

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    name = fields.Char(string='Référence')
    partner = fields.Many2one('res.partner', string="Fournisseur", required=True, track_visibility='always')
    purchases = fields.Many2one('purchase.order', string="Achats", track_visibility='always',
                                default=lambda self: self.env['purchase.order'].search([('partner_id', '=', 2)]))
    currency_id = fields.Many2one('res.currency', string='Devise achat',
                                  default=lambda self: self.env.company.currency_id.id)
    payment_instance_id = fields.Many2one('purchase.encaissement', string='Paiements additionnel',
                                          track_visibility='always')
    payment_id = fields.Many2one('account.payment', string='Paiements', track_visibility='always')
    amount = fields.Float(string="Montant", track_visibility='always')
    amount_taux = fields.Float(string="Taux paiement", track_visibility='always')
    edit_rate = fields.Float(string="Taux de conversion", compute="_compute_rate", store=True)
    company_curreny_bool = fields.Boolean()
    company_id = fields.Many2one('res.company', string='Société', default=lambda self: self.env.company)
    change_line = fields.One2many('partner.charge.line', 'change_id', string='Ligne de calcules',
                                  track_visibility='always')
    is_prive = fields.Boolean(default=True, track_visibility='always')
    purchase_amount = fields.Float('Montant', track_visibility='always')
    ecart_amount = fields.Float(string='Ecart')
    amount_init_currency = fields.Float(string='Montant payé en CFA avec le taux initial', track_visibility='always')
    state = fields.Selection([('draft', 'BROUILLON'), ('instance', 'INSTANCE'), ('posted', 'COMPTABILISE')],
                             string='Statut',
                             track_visibility='always', default='draft')
    libele = fields.Text(string='Libellé')
    account_move_id = fields.Many2one('account.move', string='Facture')
    add_payment = fields.Boolean(string="Faire un paiement")
    journal_id = fields.Many2one('account.journal', string='Journal')

    @api.onchange('add_payment')
    def onchange_add_payment(self):
        if self.is_prive and self.add_payment:
            self.is_prive = False

    @api.onchange('is_prive')
    def onchange_is_prive(self):
        for val in self:
            if val.is_prive:
                val.payment_id = False
                val.account_move_id = False
            else:
                val.payment_instance_id = False
                val.purchases = False

    @api.onchange('partner')
    def onchange_partner(self):
        for val in self:
            val.payment_id = False
            val.payment_instance_id = False
            val.purchases = False

    @api.onchange('payment_instance_id', 'payment_id')
    def compute_payment_paycompute_payment_pay(self):
        for val in self:
            if val.payment_instance_id:
                val.amount = val.payment_instance_id.somme_paye
                val.amount_taux = val.payment_instance_id.edit_rate
            elif val.payment_id:
                val.amount = val.payment_id.amount
                val.amount_taux = val.payment_id.edit_rate
            val.amount_init_currency = val.edit_rate * val.amount
            if val.amount_init_currency:
                if val.edit_rate > val.amount_taux:
                    if val.change_line:
                        for ln in val.change_line:
                            ln.update({'amount_gain': abs((val.amount_taux * val.amount) - val.amount_init_currency)})
                    else:
                        val.write({
                            'change_line': [(0, 0, {
                                'ref_purchases': val.name,
                                'amount_perte': 0,
                                'amount_gain': abs((val.amount_taux * val.amount) - val.amount_init_currency),
                            })]
                        })
                else:
                    if val.change_line:
                        for ln in val.change_line:
                            ln.update({'amount_perte': abs((val.amount_taux * val.amount) - val.amount_init_currency)})
                    else:
                        val.write({
                            'change_line': [(0, 0, {
                                'ref_purchases': val.name,
                                'amount_perte': abs(val.amount_init_currency - (val.amount_taux * val.amount)),
                                'amount_gain': 0,
                            })]
                        })
                # val.amount_taux = val.payment_id.edit_rate

    @api.onchange('amount_taux', 'amount')
    def compute_line_add_payment(self):
        for val in self:
            val.amount_init_currency = val.edit_rate * val.amount
            if val.edit_rate > val.amount_taux:
                if val.change_line:
                    for ln in val.change_line:
                        ln.update({
                            'amount_gain': abs((val.amount_taux * val.amount) - val.amount_init_currency),
                            'amount_perte': 0
                        })
                else:
                    val.write({
                        'change_line': [(0, 0, {
                            'ref_purchases': val.name,
                            'amount_perte': 0,
                            'amount_gain': abs((val.amount_taux * val.amount) - val.amount_init_currency),
                        })]

                    })
            else:
                if val.change_line:
                    for ln in val.change_line:
                        ln.update({
                            'amount_perte': abs((val.amount_taux * val.amount) - val.amount_init_currency),
                            'amount_gain': 0
                        })
                else:
                    val.write({

                        'change_line': [(0, 0, {
                            'ref_purchases': val.name,
                            'amount_perte': abs(val.amount_init_currency - (val.amount_taux * val.amount)),
                            'amount_gain': 0,
                        })]

                    })

    @api.onchange('purchases', 'account_move_id')
    def onchange_purchases(self):
        for val in self:
            val.currency_id = val.purchases.currency_id or val.account_move_id.currency_id
            val.purchase_amount = val.purchases.amount_total or val.account_move_id.amount_total
            if val.currency_id.name == val.company_id.currency_id.name:
                val.company_curreny_bool = True
                val.edit_rate = 1
            else:
                val.edit_rate = val.purchases.edit_rate or val.account_move_id.rate
                val.company_curreny_bool = False

    def add_to_tracking(self):
        """ permet d'ajouter au suivi additionnel"""
        tracking_obj = self.env['tracking.partner'].sudo()
        for val in self:
            action = {
                'partner': val.partner.id,
                'reference': val.name,
                'designation': 'Change',
                'libele_op': val.libele,
                'date': self._default_time_utc(),
                'payment_ref': str(val.id) + 'CHAN',
                'partner_type': 'vendor'

            }
            if val.is_prive:
                val.state = 'instance'
            if val.edit_rate > val.amount_taux:

                action.update({'amount_currency': val.change_line.amount_gain})
                if not val.is_prive:
                    action.update({'not_instance': True})
                tracking_obj.create(action)
            else:
                action.update({'amount_currency': val.change_line.amount_perte})

                if not val.is_prive:
                    action.update({'not_instance': True})
                tracking_obj.create(action)

    def action_to_count(self):
        """permet de comptabiliser le gain ou la perte constates"""
        account_attente = self.env['account.account'].search([('code', '=', 401100)])
        account_gain = self.env['account.account'].search([('code', '=', 776000)])
        # expense_currency_exchange_account_id
        account_pert = self.env['account.account'].search([('code', '=', 676000)])
        journal_exchange = self.env['account.journal'].search([('code', '=', 'EXCH')])  # currency_exchange_journal_id
        # journal_exchange0 = self.env['ir.config_parameter'].sudo().get_param('income_currency_exchange_account_id')

        all_lines = []
        for val in self:
            if len(val.change_line) >= 2:
                raise ValidationError(_('la ligne de gain ou de perte ne doit pas être supérieur à 1'))
            else:
                val.state = 'posted'
                vals = {
                    'ref': val.name,
                    'change_partner_id': val.id,
                    'change': True
                }
                if val.add_payment:
                    self.create_payment()
                if val.edit_rate > val.amount_taux:

                    line = (0, 0,
                            {
                                'account_id': account_gain.id,
                                'partner_id': val.partner.id,
                                'name': val.libele,
                            }
                            )
                    all_lines.append(line)
                    line = (0, 0,
                            {
                                'account_id': account_attente.id,
                                'partner_id': val.partner.id,
                                'name': val.libele,
                            }
                            )
                    all_lines.append(line)
                    vals.update(
                        {'journal_id': journal_exchange.id}
                    )
                elif val.edit_rate < val.amount_taux:
                    line = (0, 0,
                            {
                                'account_id': account_pert.id,
                                'partner_id': val.partner.id,
                                'name': val.libele,
                            }
                            )
                    all_lines.append(line)
                    line = (0, 0,
                            {
                                'account_id': account_attente.id,
                                'partner_id': val.partner.id,
                                'name': val.libele,
                            }
                            )
                    all_lines.append(line)
                    vals.update(
                        {'journal_id': journal_exchange.id}
                    )
                else:
                    raise ValidationError(_('impossible, pas de perte ou de gain'))
            vals.update(
                {'line_ids': all_lines}
            )
            self.env['account.move'].create(vals)
            self.add_to_tracking()
        # notification = {
        #     'type': 'ir.actions.client',
        #     'tag': 'display_notification',
        #     'params': {
        #         'title': ('Informations'),
        #         'message': 'la ligne a été créée avec succès',
        #         'type': 'success',  # types: success,warning,danger,info
        #         'sticky': True,  # True/False will display for few seconds if false
        #     },
        # }
        # return notification

    def create_payment(self):
        for payment in self:
            paired_payment = {
                'journal_id': payment.journal_id.id,
                'destination_journal_id': payment.journal_id.id,
                'move_id': None,
                'partner_id': payment.partner.id,
                'amount': abs(payment.amount),
                'date': payment.create_date,
                'payment_type': 'outbound',
                'partner_type': 'supplier',
                'is_internal_transfer': False,
                'from_change': True,
                'amount_init': payment.edit_rate
            }

            if payment.currency_id:
                paired_payment.update({'currency_id': payment.currency_id.id, 'edit_rate': payment.amount_taux})
                payment.currency_id.rate_ids[-1].write({'inverse_company_rate': payment.amount_taux})
            return self.env['account.payment'].sudo().create(paired_payment)

    def put_to_draft(self):
        """mettre une change en brouillon"""
        for val in self:
            if val.is_prive:
                tracking = self.env['tracking.partner'].search([('reference', '=', val.name)])
                if tracking:
                    tracking.unlink()
                val.state = 'draft'
            else:
                account_move = self.env['account.move'].search([('change_partner_id', '=', val.id)])
                if account_move.state == 'posted':
                    raise ValidationError(_('impossible de mettre une change comptabilisée en brouillon !'))
                elif account_move.state == 'draft':
                    account_move.unlink()
                    val.state = 'draft'

    def open_journal_change(self):
        """ouvre la ligne de change comptabiliser a partir de la change"""
        move_id = self.env['account.move'].search([('change_partner_id', '=', self.id)])
        action = {
            'type': 'ir.actions.act_window',
            'name': 'journal de change',
            'view_mode': 'tree,form',
            'view_type': 'form',
            'res_model': 'account.move',
            'view_id': False,
        }

        domain = ([('change_partner_id', '=', self.id)])
        action['domain'] = domain
        return action

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('partner.charge')
        return super(partnerCharge, self).create(vals)

    def unlink(self):
        for val in self:
            if val.state != 'draft':
                raise ValidationError(_('impossible de supprimer une change comptabilisée !'))
            else:
                return super(partnerCharge, self).unlink()


class partnerChargeLine(models.Model):
    _name = "partner.charge.line"

    ref_purchases = fields.Char(string="Reference")
    amount = fields.Float(string="Montant")
    date = fields.Date(string="Date")
    amount_perte = fields.Float(string="Perte")
    amount_gain = fields.Float(string="Gain")
    change_id = fields.Many2one('partner.charge', string='Changes')

    def action_validate(self):
        pass
