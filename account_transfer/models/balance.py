from odoo import fields, models


class BalanceForm (models.Model):
    _name = "balance.form"
    _description = "Balance"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    reference = fields.Char(string='Reference du mouvement', readonly=True)
    client = fields.Many2one('res.partner', string="Clients", tracking=True)
    debit = fields.Integer(string='Débit', readonly=True)
    credit = fields.Integer(string='Crédit', readonly=True)
    balance = fields.Integer(string='Balance', readonly=True)
    date = fields.Date(string='Date', tracking=True, readonly=True)
    montant_devise = fields.Char(string='Montant devise')
    state = fields.Selection([
        ('payment', 'Paiement'),
        ('transfer', 'Transfert')], string="Status")
    country = fields.Selection([
        ('lebanon', 'Liban'),
        ('france', 'France'),
        ('dubai', 'Dubai')], string="Pays destinataire")
    rate = fields.Char(string="Taux fait au client")