from math import floor
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class VendorPayment(models.Model):
    _name = "vendor.payment"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Paiement Fournisseurs"
    _rec_name = 'reference'

    def default_current_date(self):
        return fields.Date.context_today(self)

    reference = fields.Char(string='Reference', readonly=True, required=True, default=lambda self: 'Nouveau')

    # Informations générale
    date = fields.Date(string='Date', required=True, default=default_current_date, tracking=True)
    vendor = fields.Many2one('res.partner', string="Fournisseur", required=True, tracking=True)

    # Informations du transferts
    amount = fields.Integer(string='Montant en CFA', tracking=True)
    currency = fields.Integer(string='Taux de change', default="656", required=True)
    currency_code = fields.Selection([
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('CFA', 'CFA')], string="Devise de réception", default='USD', required=True)

    # Autres
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Validé')], default='draft', required=True, string="Status")

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].sudo().next_by_code('vendor.payment')
        result = super(VendorPayment, self).create(vals)
        return result

    @api.depends('amount', 'currency_code', 'currency')
    def _calculate_currency(self):
        for record in self:
            calcul = record.amount / record.currency
            calcul = floor(calcul)
            display = format(calcul) + ' ' + str(record.currency_code)
            record.calculated_currency = display

    @api.depends('total_gain')
    def _line_gain_implement(self):
        for rec in self:
            rec.gain_currency = "{:,}".format(rec.total_gain) + ' ' + 'CFA'

    def send_to_balance(self):
        self.state = 'confirm'
        to_balance_form = self.env['vendor.balance']
        existing_line = to_balance_form.search([('reference', '=', self.reference)], limit=1)
        if not existing_line:
            to_balance_form.create({
                'reference': self.reference,
                'date': self.date,
                'vendor': self.vendor.id,
                'credit': self.amount,
                'balance': - self.amount,
                'state': 'payment',
            })

        for cash in self:
            to_cash_flow = self.env['cash.flow']
            to_cash_flow.create({
                'date': cash.date,
                'operation_type': 'in',
                'description': "Créé à partir du paiement : " + cash.reference + " / Fournisseur : " + str(cash.vendor.name),
                'amount': - cash.amount,
                'state': 'confirm',
                'operation_id': cash.reference,
                })

    def back_draft(self):
        self.state = 'draft'
        for cash in self:
            to_cash_flow = self.env['cash.flow']
            delete_to = to_cash_flow.search([
                ('operation_id', '=', cash.reference),
            ])
            delete_to.unlink()

        to_vendor_balance = self.env['vendor.balance']
        to_delete = to_vendor_balance.search([
            ('reference', '=', self.reference),
        ])
        to_delete.unlink()

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError('Vous ne pouvez pas supprimer une opération au status confirmé')
            return super(VendorPayment, self).unlink()
