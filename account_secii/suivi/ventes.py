# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

from odoo.tools import float_round

import pytz


def get_price_in_xof(currency_id, company_id, date):
    currency_name = currency_id.name
    if currency_name != 'XOF':
        rates = currency_id._get_rates(company_id, date)
        rate_value = 1
        if rates:
            for value in rates.values():
                rate_value = 1 / value
        return rate_value
    else:
        return 1


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    create_invoice = fields.Boolean(string='Créer facture', default=True)

    @api.onchange('is_prive')
    def onchange_is_prive(self):
        search_name_picking = self.env['stock.picking'].search([('origin', '=', self.name)])
        if search_name_picking:
            search_name_picking.write({'is_prive': self.is_prive})

        search_ref_move = self.env['stock.move'].sudo().search([('origin', '=', self.name)])
        if search_ref_move:
            for move in search_ref_move:
                move.write({'is_prive': self.is_prive})

                search_ref_move_line = self.env['stock.move.line'].sudo().search([('move_id', '=', move.id)])
                if search_ref_move_line:
                    for line in search_ref_move_line:
                        line.write({'is_prive': self.is_prive})

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.is_prive:
            self.update_private_record()
        return res

    def update_private_record(self):
        for val in self:
            action = {
                'partner': val.partner_id.id,
                'reference': val.name,
                'designation': 'Vente',
                'date': self._default_time_utc(),
                'purchase_ref': str(val.id) + 'VEN',
                'partner_type': 'customer',

            }
            tracking_obj = self.env['tracking.partner'].sudo().search([('purchase_ref', '=', str(val.id) + 'VEN')])
            if tracking_obj:
                if val.currency_id.name == 'XOF':
                    action.update({'amount_currency': val.amount_total})
                    tracking_obj.write(action)
            else:
                if val.currency_id.name == 'XOF':
                    action.update({'amount_currency': val.amount_total})
                self.env['tracking.partner'].sudo().create(action)


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def create_invoices(self):
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
        for sale in sale_orders:
            if sale.is_prive:
                raise ValidationError(
                    _("Vous ne pouvez pas créer une facture pour une commande mis en instance !"))
        return super(SaleAdvancePaymentInv, self).create_invoices()
