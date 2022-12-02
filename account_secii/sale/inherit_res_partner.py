# -*- coding: utf-8 -*-

from odoo import fields, models, api


class InheritResPartner(models.Model):
    _inherit = 'res.partner'

    sale_order_nbr = fields.Integer(string='Nbres', compute='_compute_sale_order_count_user')
    plafond = fields.Monetary(string='Plafond Client', default=0)
    reste_payer = fields.Monetary(string='Reste à Payer', compute="rst_a_payer")
    test = fields.Monetary(string="Crédit Initial", compute='recherche_reste_a_payer')
    credit_client = fields.Monetary(string="Crédit Disponible")

    def recherche_reste_a_payer(self):
        if self.plafond > 0 and self.credit_client == 0:
            self.test = self.plafond - self.reste_payer

        elif self.plafond > 0 and self.credit_client > 0:
            self.test = self.plafond - self.reste_payer
        else:
            self.test = 0

    def rst_a_payer(self):
        self.reste_payer = 0
        self.credit_client = 0
        for so in self:
            montant_cumule = sum(self.env['sale.order'].sudo().search(
                [('partner_id', '=', so.id), ('state', 'in', ('sale', 'done'))]).mapped(
                'amount_total'))
            print('MC', montant_cumule)
            cumul = sum(self.env['secii.encaissement'].sudo().search(
                [('partenaire', '=', so.id)]).mapped('somme_paye'))
            print('CUM', cumul)
            so.reste_payer = montant_cumule - cumul
            print('RAP', so.reste_payer)
            if so.plafond > 0 and so.reste_payer < 0:
                so.credit_client = abs(so.reste_payer)
                so.reste_payer = 0
            else:
                so.credit_client = 0

    def _compute_sale_order_count(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        # filter without private
        sale_order_groups = self.env['sale.order'].read_group(
            domain=[('partner_id', 'in', all_partners.ids)],
            fields=['partner_id'], groupby=['partner_id']
        )
        partners = self.browse()
        for group in sale_order_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.sale_order_count += group['partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).sale_order_count = 0

    def _compute_sale_order_count_user(self):
        # retrieve all children partners and prefetch 'parent_id' on them
        all_partners = self.with_context(active_test=False).search([('id', 'child_of', self.ids)])
        all_partners.read(['parent_id'])

        # filter without private
        sale_order_groups = self.env['sale.order'].read_group(
            domain=[('partner_id', 'in', all_partners.ids), ('is_prive', '=', False)],
            fields=['partner_id'], groupby=['partner_id']
        )
        partners = self.browse()
        for group in sale_order_groups:
            partner = self.browse(group['partner_id'][0])
            while partner:
                if partner in self:
                    partner.sale_order_nbr += group['partner_id_count']
                    partners |= partner
                partner = partner.parent_id
        (self - partners).sale_order_nbr = 0
