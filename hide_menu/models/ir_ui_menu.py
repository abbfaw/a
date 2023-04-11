# -*- coding: utf-8 -*-

from odoo import models, api, tools


class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    """
    Le décorateur @tools.ormcache est utilisé pour mettre en cache les résultats 
    de la fonction _visible_menu_ids en fonction des identifiants des groupes de 
    l'utilisateur et de l'argument de débogage
    """
    @api.model
    @tools.ormcache('frozenset(self.env.user.groups_id.ids)', 'debug')
    def _visible_menu_ids(self, debug=False):
        menus = super(IrUiMenu, self)._visible_menu_ids(debug)
        if self.env.user.hide_menu_ids and not self.env.user.has_group('base.group_system'):
            for rec in self.env.user.hide_menu_ids:
                menus.discard(rec.id)
            return menus
        return menus
