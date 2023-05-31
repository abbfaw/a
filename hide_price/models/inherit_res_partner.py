from odoo import api, fields, models
from odoo.http import request
# from twilio.rest import Client


class ResPartnerInherit(models.Model):
    _inherit = 'res.partner'

    ville = fields.Selection([('abidjan', "Abidjan"), ('interieur', "Intérieur du pays")],
                             string="Lieu de livraison")

    commune_id = fields.Many2one('res.commune', store=True, index=True)
    ville_id = fields.Many2one('res.ville', store=True, index=True)

    plus_detail = fields.Char(string="Plus de détails")
    from_web = fields.Boolean(store=True)
    visitors = fields.Boolean(store=True)
