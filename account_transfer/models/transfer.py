from math import floor
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError


class TransferForm(models.Model):
    _name = "transfer.form"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Transfert"
    _rec_name = 'reference'

    def default_current_date(self):
        return fields.Date.context_today(self)

    reference = fields.Char(string='Reference', readonly=True, required=True, default=lambda self: 'Nouveau')

    # Informations générale
    date = fields.Date(string='Date', required=True, default=default_current_date, tracking=True)
    operation_type = fields.Selection([
        ('transfer', 'Transfert'),
        ('payment', 'Paiement')], string="Type d'opération", default='transfer')
    client = fields.Many2one('res.partner', string="Clients", required=True, tracking=True)
    is_local = fields.Boolean(string="Entrée en caisse ?")
    add_payment = fields.Boolean(string="Créer le paiement ?")

    # Informations fournisseur
    vendor_tree = fields.One2many('vendor.tree', inverse_name='vendor_tree_id', string='Vendors')

    # Informations du transferts
    amount = fields.Integer(string='Montant en CFA', tracking=True)
    money_type = fields.Selection([
        ('cash', 'Espèce'),
        ('bank', 'Chèque')], string="Moyen de paiement", default='cash')
    country = fields.Selection([
        ('lebanon', 'Liban'),
        ('france', 'France'),
        ('dubai', 'Dubai')], string="Pays destinataire", default='lebanon')
    currency = fields.Integer(string='Taux de change', default="656", required=True)
    currency_code = fields.Selection([
        ('USD', 'USD'),
        ('EUR', 'EUR'),
        ('CFA', 'CFA')], string="Devise de réception", default='USD', required=True)
    calculated_currency = fields.Char(string='Montant en devise envoyée', compute='_calculate_currency')
    total_gain = fields.Integer(compute='_gain_calcul')
    gain_currency = fields.Char(string='Bénéfice total sur la transaction', compute='_line_gain_implement')

    # Informations chèque
    check_num = fields.Char(string="Numéro du chèque")
    bank_ref = fields.Char(string="Banque du client")
    check_attach = fields.Many2many(
        'ir.attachment',
        'check_doc_rel',
        string="Photo du chèque", tracking=True
    )

    # Autres
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Validé')], default='draft', required=True, string="Status")

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].sudo().next_by_code('transfer.form')
        result = super(TransferForm, self).create(vals)
        return result

    @api.depends('amount', 'currency_code', 'currency')
    def _calculate_currency(self):
        for record in self:
            calcul = record.amount / record.currency
            calcul = floor(calcul)
            display = format(calcul) + ' ' + str(record.currency_code)
            record.calculated_currency = display

    @api.depends('vendor_tree')
    def _gain_calcul(self):
        for rec in self:
            rec.total_gain = sum(rec.vendor_tree.mapped('gain'))

    @api.depends('total_gain')
    def _line_gain_implement(self):
        for rec in self:
            rec.gain_currency = "{:,}".format(rec.total_gain) + ' ' + 'CFA'

    def send_to_balance(self):
        self.state = 'confirm'
        to_balance_form = self.env['balance.form']
        existing_line = to_balance_form.search([('reference', '=', self.reference)], limit=1)
        ope_type = self.operation_type
        if not existing_line:
            if ope_type == "transfer":
                to_balance_form.create({
                    'reference': self.reference,
                    'date': self.date,
                    'client': self.client.id,
                    'credit': self.amount,
                    'balance': - self.amount,
                    'montant_devise': self.calculated_currency,
                    'state': self.operation_type,
                    'rate': self.currency,
                    'country': self.country,
                })
            elif ope_type == "payment":
                to_balance_form.create({
                    'reference': self.reference,
                    'date': self.date,
                    'client': self.client.id,
                    'debit': self.amount,
                    'balance': self.amount,
                    'montant_devise': self.calculated_currency,
                    'state': self.operation_type,
                })

        if self.add_payment:
            to_balance_form.create({
                'reference': self.reference,
                'date': self.date,
                'client': self.client.id,
                'debit': self.amount,
                'balance': self.amount,
                'montant_devise': self.calculated_currency,
                'state': 'payment',
            })

        for rec in self:
            to_vendor_mouv = self.env['vendor.mouv']
            for line in rec.vendor_tree:
                to_vendor_mouv.create({
                    'date': rec.date,
                    'client': rec.client.id,
                    'amount': line.used_amount,
                    'get_vendor': line.vendor.id,
                    'internal_id': line.vendor_id.internal_reference,
                    'purchased_rate': line.vendor_rate,
                    'sold_rate': rec.currency,
                    'gain': line.gain,
                })

        for cash in self:
            to_cash_flow = self.env['cash.flow']
            if cash.is_local or cash.add_payment:
                to_cash_flow.create({
                    'date': cash.date,
                    'operation_type': 'in',
                    'description': "Créé à partir de l'opération : " + cash.reference + " / Client : " + str(
                        cash.client.name),
                    'amount': cash.amount,
                    'state': 'confirm',
                    'operation_id': cash.reference,
                })

        for venbal in self:
            for vnbl in self.vendor_tree:
                to_vendor_balance = self.env['vendor.balance']
                to_vendor_balance.create({
                    'reference': self.reference,
                    'date': venbal.date,
                    'vendor': vnbl.vendor.id,
                    'debit': vnbl.used_amount,
                    'balance': vnbl.used_amount,
                    'state': 'transfer',
                })

        for gain_flow in self:
            to_gain_flow = self.env['gain.flow']
            to_gain_flow.create({
                'operation_id': self.reference,
                'date': gain_flow.date,
                'client': gain_flow.client.id,
                'amount': gain_flow.total_gain,
                'description': "Créé à partir de l'opération : " + gain_flow.reference + " / Client : " + str(
                    gain_flow.client.name),
                'operation_type': 'gain',
                'state': 'confirm'
            })

    @api.constrains('amount', 'vendor_tree')
    def _check_transfer_amount(self):
        for left in self:
            all_transfers = sum(left.vendor_tree.mapped('used_amount'))
            if all_transfers > left.amount:
                raise ValidationError(
                    "Le montant utilisé ne peut pas être supérieur au montant à transféré !")

    @api.constrains('amount', 'vendor_tree')
    def _recheck_transfer_amount(self):
        for left in self:
            all_transfers = sum(left.vendor_tree.mapped('used_amount'))
            if all_transfers < left.amount and left.operation_type != 'payment':
                raise ValidationError(
                    "Le montant utilisé ne peut pas être inférieur au montant à transféré !")

    def back_draft(self):
        self.state = 'draft'
        to_vendor_mouv = self.env['vendor.mouv']
        for rec in self:
            for line in rec.vendor_tree:
                to_delete = to_vendor_mouv.search([
                    ('date', '=', rec.date),
                    ('client', '=', rec.client.id),
                    ('amount', '=', line.used_amount),
                    ('purchased_rate', '=', line.vendor_rate),
                    ('sold_rate', '=', rec.currency),
                    ('gain', '=', line.gain),
                    ('get_vendor', '=', line.vendor.id),
                    ('internal_id', '=', line.vendor_id.internal_reference),
                ])
                to_delete.unlink()

        to_balance_form = self.env['balance.form']
        to_delete = to_balance_form.search([
            ('reference', '=', self.reference),
        ])
        to_delete.unlink()

        to_vendor_balance = self.env['vendor.balance']
        to_delete = to_vendor_balance.search([
            ('reference', '=', self.reference),
        ])
        to_delete.unlink()

        to_gain_flow = self.env['gain.flow']
        to_delete = to_gain_flow.search([
            ('operation_id', '=', self.reference),
        ])
        to_delete.unlink()

        to_cash_flow = self.env['cash.flow']
        to_delete = to_cash_flow.search([
            ('operation_id', '=', self.reference),
        ])
        to_delete.unlink()

    def unlink(self):
        for record in self:
            if record.state != 'draft':
                raise UserError('Vous ne pouvez pas supprimer une opération au status confirmé')
            return super(TransferForm, self).unlink()


class VendorTree(models.Model):
    _name = "vendor.tree"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Taux Fournisseurs"

    def _get_vendor_w_credit(self):
        return self.env['vendor.form'].sudo().search([('state', '=', 'out')])

    vendor_id = fields.Many2one('vendor.form', string="Fornisseur", tracking=True,
                                domain=[('state', '=', 'confirm')])
    vendor = fields.Many2one('res.partner', string="Fournisseur", compute='_get_vendor_from_id', tracking=True,
                             store=True)
    vendor_date = fields.Date(string='Date', compute='_get_vendor_date', tracking=True)
    vendor_rate = fields.Integer(string='Taux fournisseur', compute='_get_vendor_rate', tracking=True, store=True)
    used_amount = fields.Integer(string='Montant utilisé', tracking=True)
    vendor_tree_id = fields.Many2one('transfer.form', string='Vendor Tree')
    gain = fields.Integer(string='Bénéfices', compute='_line_gain_calculate')

    @api.depends('vendor_id')
    def _get_vendor_from_id(self):
        for rec in self:
            vendor_mouv_lines = self.env['vendor.form'].search([('internal_reference', '=',
                                                                 rec.vendor_id.internal_reference)])
            rec.vendor = vendor_mouv_lines.mapped('vendor')

    @api.depends('vendor_id')
    def _get_vendor_rate(self):
        for rec in self:
            for line in self.vendor_tree_id:
                if line.state == 'draft':
                    vendor_rate_lines = self.env['vendor.form'].search([('internal_reference', '=',
                                                                         rec.vendor_id.internal_reference)])
                    rec.vendor_rate = vendor_rate_lines.currency
                else:
                    rec.vendor_rate = rec.vendor_rate

    @api.depends('vendor_id')
    def _get_vendor_state(self):
        for rec in self:
            vendor_state_lines = self.env['vendor.form'].search([('internal_reference', '=',
                                                                  rec.vendor_id.internal_reference)])
            rec.vendor_rate = vendor_state_lines.state

    @api.onchange('used_amount', 'vendor_tree_id')
    def _line_gain_calculate(self):
        for rec in self:
            currency_value = rec.vendor_tree_id.currency
            rec.gain = (rec.vendor_tree_id.currency - rec.vendor_rate) * (rec.used_amount / currency_value)
