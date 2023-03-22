from odoo import fields, models


class VendorBalance (models.Model):
    _name = "vendor.balance"
    _description = "Balance Fournisseurs"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference = fields.Char(string='Reference du mouvement', readonly=True)
    vendor = fields.Many2one('res.partner', string="Fournisseur", tracking=True)
    debit = fields.Integer(string='Débit', readonly=True)
    credit = fields.Integer(string='Crédit', readonly=True)
    balance = fields.Integer(string='Balance', readonly=True)
    date = fields.Date(string='Date', tracking=True, readonly=True)
    montant_devise = fields.Char(string='Montant devise')
    state = fields.Selection([
        ('payment', 'Paiement'),
        ('transfer', 'Dette')], string="Status")
    country = fields.Selection([
        ('lebanon', 'Liban'),
        ('france', 'France'),
        ('dubai', 'Dubai')], string="Pays destinataire")
    rate = fields.Char(string="Taux fait au client")