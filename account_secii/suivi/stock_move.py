# -*- coding: utf-8 -*-

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    is_prive = fields.Boolean(string="En instance")

    @api.model
    def create(self, vals_list):
        private_purchase = self.env['purchase.order'].search([('name', '=', vals_list.get('origin'))]).is_prive
        if private_purchase:
            vals_list.update({'is_prive': private_purchase})
        return super(StockMove, self).create(vals_list)


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    is_prive = fields.Boolean(string="En instance", default=False)

    @api.model
    def create(self, vals_list):
        private_move = self.env['stock.move'].search([('id', '=', vals_list.get('move_id'))]).is_prive
        if private_move:
            vals_list.update({'is_prive': private_move})
        return super(StockMoveLine, self).create(vals_list)

    def update_move_line_date(self):
        # 'context': {'default_line_ids': aquisition_list},
        return {
            'name': "Mise a jour",
            'view_mode': 'form',
            'res_model': 'update.date',
            'type': 'ir.actions.act_window',
            'target': 'new',

        }


class StockLocation(models.Model):
    _inherit = 'stock.location'

    to_receive = fields.Boolean(string='A recevoir')
