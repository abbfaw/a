# -*- coding: utf-8 -*-
from datetime import datetime

import pytz

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_round
from odoo.tools.view_validation import valid_view


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    create_invoice = fields.Boolean(string='Créer facture', default=True)
    official_quotation_id = fields.Integer(string='ID')
    official_quotation_exist = fields.Boolean(string='Quotation exist')
    statut = fields.Selection([('0_confirm', 'Action confirmation'), ('1_generate', 'Action generate')])
    add_price = fields.Boolean(string='Prix Additionnel')
    releve_client_id = fields.Many2one('purchase.synthese', string='Relevé Client')
    official_amount_total = fields.Float(string='Montant total Additionnel', store=True, compute='_amount_all_official')
    edit_rate = fields.Float(string="Taux de conversion", compute="_compute_rate", store=True)
    company_curreny_bool = fields.Boolean()
    from_instance_purchase = fields.Boolean()
    nature_operation = fields.Char(string='Nature des produits')
    ref_import = fields.Char(string="Référence d'importation")

    @api.depends('currency_id')
    @api.onchange('currency_id', 'company_id')
    def _compute_rate(self):
        for move in self:
            if move.currency_id.name == move.company_id.currency_id.name:
                move.company_curreny_bool = True
                move.edit_rate = 1
            else:
                rates = move.currency_id._get_rates(move.company_id, move.date_order.date())
                rate_value = 1
                if rates:
                    for value in rates.values():
                        rate_value = 1 / value
                move.edit_rate = rate_value
                move.company_curreny_bool = False

    @api.depends('order_line.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                line._compute_amount()
                amount_untaxed += (line.price_subtotal - line.subtotal_oficiel)
                amount_tax += (line.price_tax - self.compute_taxes_amount(line))
            currency = order.currency_id or order.partner_id.property_purchase_currency_id or self.env.company.currency_id

            order.update({
                'amount_untaxed': currency.round(amount_untaxed),
                'amount_tax': currency.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax
            })

    @api.depends('order_line.officiel_price')
    def _amount_all_official(self):
        for order in self:
            for line in order.order_line:
                tax_use = self.env['account.tax'].search([('id', '=', line.taxes_id.id)])
                order.official_amount_total += (line.subtotal_oficiel + (line.subtotal_oficiel * tax_use.amount) / 100)

    @api.onchange('order_line')
    def onchange_line_order_generate(self):
        for val in self:
            if val.from_instance_purchase:
                raise ValidationError(
                    _("Vous ne pouvez pas modifier un achat généré !"))

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

    def _compute_releve_compte_client(self):
        tracking_obj = self.env['tracking.partner'].sudo()
        for val in self:
            action = {
                'partner': val.partner_id.id,
                'reference': val.name,
                'designation': 'Achat',
                'date': self._default_time_utc(),
                'purchase_ref': str(val.id) + 'ACH',
                'partner_type': 'vendor',
                'purchase_id': val.id
            }
            if val.is_prive:
                action.update({'amount_currency': val.amount_total})
                if val.retour:
                    action.update({
                        'amount_currency': - val.amount_total,
                        'partner_type': 'customer',
                        'designation': "Retour Achat",
                                   })
                tracking_obj.create(action)

    def button_confirm(self):
        for line in self:
            if line.is_prive:
                self._compute_releve_compte_client()
                line.statut = '0_confirm'
        return super(PurchaseOrder, self).button_confirm()

    def button_cancel(self):
        for line in self:
            tracking_obj = self.env['tracking.partner'].sudo().search([('purchase_ref', '=', str(line.id) + 'ACH')])
            if tracking_obj:
                tracking_obj.unlink()
        return super(PurchaseOrder, self).button_cancel()

    def update_private_record(self):
        for val in self:
            action = {
                'partner': val.partner_id.id,
                'reference': val.name,
                'designation': 'Achat',
                'date': self._default_time_utc(),
                'purchase_ref': str(val.id) + 'ACH',
                'partner_type': 'vendor'
            }
            tracking_obj = self.env['tracking.partner'].sudo().search([('purchase_ref', '=', str(val.id) + 'ACH')])
            if tracking_obj:
                action.update({'amount_currency': val.amount_total})
                tracking_obj.write(action)

    def action_create_invoice(self):
        res = super(PurchaseOrder, self).action_create_invoice()
        for line in self:
            if line.is_prive:
                raise ValidationError(
                    _("Vous ne pouvez pas créer une facture pour une commande mis en instance !"))
            # invoice = self.env['account.move'].search([('invoice_origin', '=', line.name)])
            # if invoice:
            #     invoice.write({'rate': line.edit_rate})
        return res

    def action_generate_official_purchase(self):
        self.official_quotation_exist = True
        val = self.copy_data()
        all_values = []
        for va in val:
            if va.get('is_prive'):
                self._compute_releve_compte_client()
                self.statut = '1_generate'
                for orderline in va.get('order_line'):
                    values = orderline[2]
                    line = (0, 0, {
                        'name': values.get('name'),
                        'sequence': values.get('sequence'),
                        'product_qty': values.get('product_qty'),
                        'date_planned': values.get('date_planned'),
                        'taxes_id': values.get('taxes_id'),
                        'product_uom': values.get('product_uom'),
                        'product_id': values.get('product_id'),
                        'price_unit': values.get('officiel_price'),
                        'order_id': values.get('order_id'),
                        'account_analytic_id': values.get('account_analytic_id'),
                        'analytic_tag_ids': values.get('analytic_tag_ids'),
                        'product_packaging_id': values.get('product_packaging_id'),
                        'product_packaging_qty': values.get('product_packaging_qty'),
                        'display_type': values.get('display_type'),
                        'product_description_variants': values.get('product_description_variants'),
                        'propagate_cancel': values.get('propagate_cancel'),
                        'sale_line_id': values.get('sale_line_id')
                    })
                    all_values.append(line)

                    # créé ton dict
                quotation = {
                    'priority': va.get('priority'),
                    'partner_id': va.get('partner_id'),
                    'dest_address_id': va.get('dest_address_id'),
                    'currency_id': va.get('currency_id'),
                    'order_line': all_values,
                    'notes': va.get('notes'),
                    'partner_ref': va.get('partner_ref'),
                    'from_instance_purchase': True,
                    'fiscal_position_id': va.get('fiscal_position_id'),
                    'payment_term_id': va.get('payment_term_id'),
                    'incoterm_id': va.get('incoterm_id'),
                    'user_id': va.get('user_id'),
                    'company_id': va.get('company_id'),
                    'picking_type_id': va.get('picking_type_id'),
                    'is_prive': False,
                    'create_invoice': True
                }
                new_order = self.env['purchase.order'].create(quotation)
                self.write({'official_quotation_id': new_order.id})
                view_id = self.env.ref('purchase.purchase_order_form').id
                return {
                    'name': 'Demandes de prix',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'views': [(view_id, 'form')],
                    'res_model': 'purchase.order',
                    'view_id': view_id,
                    'type': 'ir.actions.act_window',
                    'res_id': new_order.id,
                    'target': 'current'
                }

    def create_payment_instance(self):
        if self.is_prive:
            exist = self.env['purchase.encaissement'].sudo().search(
                [('purchase_direct_payment', '=', str(self.id) + 'PUR')])
            if exist:
                exist.unlink()

            vals = {
                'partner_id': self.partner_id.id,
                'currency_id': self.currency_id.id,
                'somme_paye': float_round(self.amount_total, 2),
                'purchase_direct_payment': str(self.id) + 'PUR',
                'partner_type': 'vendor'
            }
            new_order = self.env['purchase.encaissement'].create(vals)
            view_id = self.env.ref('sale_purchase_private.encaissement_purchase_form').id
            return {
                'name': 'Paiements fournisseurs',
                'view_type': 'form',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'purchase.encaissement',
                'view_id': view_id,
                'type': 'ir.actions.act_window',
                'res_id': new_order.id,
                'target': 'current'
            }

    def open_official_quotation(self):
        view_id = self.env.ref('purchase.purchase_order_form').id
        return {
            'name': 'Demandes de prix',
            'view_type': 'form',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'purchase.order',
            'view_id': view_id,
            'type': 'ir.actions.act_window',
            'res_id': self.official_quotation_id,
            'target': 'current'
        }

    def compute_taxes_amount(self, line):
        taux = line.taxes_id.amount
        return (taux * line.subtotal_oficiel) / 100


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    show_oficiel = fields.Boolean()
    officiel_price = fields.Float(string='prix Additionnel')
    subtotal_oficiel = fields.Float(string='sous-total Additionnel', compute='_compute_subtotal_officiel')

    @api.depends('officiel_price', 'product_qty')
    def _compute_subtotal_officiel(self):
        for line in self:
            line.subtotal_oficiel = line.product_qty * line.officiel_price
