from math import floor
from odoo import api, fields, models


class VendorForm(models.Model):
    _name = "vendor.form"
    _description = "Fournisseur"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'vendor'

    def default_current_date(self):
        return fields.Date.context_today(self)

    reference = fields.Char(compute='_compute_name', store=True, readonly=True)
    internal_reference = fields.Char(string='Reference', readonly=True, required=True, default=lambda self: 'Nouveau')
    date = fields.Date(string='Date', required=True, default=default_current_date, tracking=True)
    vendor = fields.Many2one('res.partner', string="Fournisseur", required=True, tracking=True)
    currency = fields.Integer(string="Taux d'achat")
    get_moves = fields.Many2many('vendor.mouv', string="Mouvements fournisseurs", compute='_compute_moves')
    used_amount = fields.Integer(string="Montant réservé", tracking=True)

    # Autres
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Validé')], readonly=True, copy=False, index=True, track_visibility='onchange',
                            default='draft', string="Status")

    @api.depends('vendor', 'currency', 'date')
    def _compute_name(self):
        for record in self:
            partner_name = record.vendor.name if record.vendor else ''
            record.reference = f"{partner_name} / {record.currency} / {record.date}"

    @api.model
    def create(self, vals):
        vals['internal_reference'] = self.env['ir.sequence'].next_by_code('vendor.form')
        result = super(VendorForm, self).create(vals)
        return result

    @api.depends('internal_reference')
    def _compute_moves(self):
        for rec in self:
            if rec.internal_reference:
                rec.get_moves = self.env['vendor.mouv'].search([('internal_id', '=', rec.internal_reference)])
            else:
                rec.get_moves = False

    def go_validate(self):
        self.state = 'confirm'

    def back_draft(self):
        self.state = 'draft'


class VendorMouvements(models.Model):
    _name = 'vendor.mouv'
    _description = 'Mouvements des fournisseurs'

    date = fields.Date(string='Date', tracking=True, readonly=True)
    get_vendor = fields.Many2one('res.partner', string="Fournisseur", tracking=True)
    client = fields.Many2one('res.partner', string="Clients", tracking=True)
    purchased_rate = fields.Integer(string="Taux d'achat", tracking=True)
    sold_rate = fields.Integer(string="Taux de vente", tracking=True)
    gain = fields.Integer(string="Bénéfice Total", tracking=True)
    amount = fields.Integer(string='Montant en CFA', tracking=True)
    currency_id = fields.Integer(string='Taux', tracking=True)
    internal_id = fields.Char(string='Référence interne')
