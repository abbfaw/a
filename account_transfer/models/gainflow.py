from math import floor
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class GainFlow(models.Model):
    _name = "gain.flow"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Bénéfices"
    _rec_name = 'reference'

    def default_current_date(self):
        return fields.Date.context_today(self)

    @api.model
    def create(self, vals):
        vals['reference'] = self.env['ir.sequence'].next_by_code('gain.flow')
        result = super(GainFlow, self).create(vals)
        return result

    reference = fields.Char(string='Reference', readonly=True, required=True, default=lambda self: 'Nouveau')
    client = fields.Many2one('res.partner', string="Clients", tracking=True)
    date = fields.Date(string='Date', required=True, default=default_current_date, tracking=True)
    operation_type = fields.Selection([
        ('gain', 'Bénéfices'),
        ('out', 'Sortie')], string="Type d'opération", default='out')
    description = fields.Text(string="Libéllé de l'opération")
    amount = fields.Integer(string="Somme")
    tree_amount = fields.Integer(string="Somme", compute='_compute_amount')
    operation_id = fields.Char(string="Reference Opération")

    # Autres
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('confirm', 'Validé')], readonly=True, copy=False, default='draft', string="Status")

    @api.constrains('amount', 'operation_type')
    def _compute_amount(self):
        for record in self:
            if record.operation_type == 'gain':
                record.tree_amount = record.amount
            else:
                record.tree_amount = - record.amount

    def go_validate(self):
        self.state = 'confirm'

    def back_draft(self):
        self.state = 'draft'