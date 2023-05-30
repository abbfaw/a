# -*- coding: utf-8 -*-
from odoo import models, fields


class PosOrder(models.Model):
    _inherit = 'pos.config'

    hide_refund = fields.Boolean(string='Ne par Autoriser des Retour (Refund)')

# $('.control-button').find('.fa-undo').show();