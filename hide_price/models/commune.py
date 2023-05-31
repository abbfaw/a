from odoo import api, fields, models


class CommuneResPartner(models.Model):
    _name = 'res.commune'
    _description = "Communes de la ville d'Abidjan"

    name = fields.Char(string='Commune')
