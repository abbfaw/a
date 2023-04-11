# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    hide_menu_ids = fields.Many2many('ir.ui.menu', 'ir_ui_hide_menu_rel', 'uid', 'menu_id',
                                     string='Menus à masquer')

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        self.self.clear_caches()  # vide les caches lorsque les paramètres de l'utilisateur sont modifiés
        return res
