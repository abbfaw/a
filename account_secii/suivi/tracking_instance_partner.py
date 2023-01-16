from lxml import etree
from odoo import fields, models, api


class TrackingInstancePartner(models.Model):
    _name = 'tracking.partner'
    _order = 'create_date desc'

    date = fields.Date(string='Date')
    partner = fields.Many2one('res.partner', string="Fournisseur", readonly=True)
    reference = fields.Char(string='Réference')
    currency_id = fields.Many2one('res.currency', string='Devise', default=lambda self: self.env.company.currency_id.id)
    amount_currency = fields.Float(string='Montant')
    debit = fields.Monetary(string='Débit', currency_field='currency_id')
    credit = fields.Monetary(string='Crédit', currency_field='currency_id')
    payment_ref = fields.Char(string='Réference paiement')
    purchase_ref = fields.Char(string='Réference achat')
    currency_amount = fields.Monetary(string='TEST')
    designation = fields.Char(string='Désignation')
    nature_operation = fields.Char(string='Nature des produits')
    ref_import = fields.Char(string="Référence d'importation")
    payment_method = fields.Selection([('espece', 'Espèce'), ('bank', 'Banque'), ('box', 'Payer depuis la caisse')],
                                      string="Type d'opérations")
    libele_op = fields.Text(string="Libellé d'opérations", default=' ')
    move_id = fields.Many2one('account.move', string='Facture lié')
    payment_id = fields.Many2one('account.payment', string='Paiement lié')
    not_instance = fields.Boolean()
    correspondance = fields.Char(string='Référence', compute='_compute_correspondance',
                                 help='permet de faire le lien entre un achat prive et normal')
    purchase_id = fields.Many2one('purchase.order', string='Achat', help='relation achat')
    partner_type = fields.Selection([('customer', 'Client'), ('vendor', 'Fournisseur')])
    sale_id = fields.Many2one('purchase.order', string='vente', help='relation vente')
    move_line_id = fields.Many2one('account.move.line', string='move line')
    balance = fields.Float(string='Balance')

    def _compute_correspondance(self):
        purchase = self.env['purchase.order']
        sale = self.env['sale.order']
        for line in self:
            purchase_1 = line.purchase_id.name
            purchase_2 = line.move_id.invoice_origin
            if purchase_1:
                purchase_official = purchase.search([('id', '=', line.purchase_id.official_quotation_id)])
                line.correspondance = 'Achat additionnel ' + purchase_1 + ' - ' + purchase_official.name + ' : ' +\
                                      str(line.purchase_id.amount_total + purchase_official.amount_total) + ' - ' + \
                                      str(purchase_official.amount_total)
            elif purchase_2:
                purchase_official = purchase.search([('name', '=', purchase_2)])
                private_purchase = purchase.search([('official_quotation_id', '=', purchase_official.id)])
                line.correspondance = 'Achat normal ' + private_purchase.name + ' - ' + purchase_official.name + ' : ' + str(
                    private_purchase.amount_total + purchase_official.amount_total) + ' - ' + \
                                      str(private_purchase.amount_total)
            else:
                line.correspondance = ' '

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super().fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        self.move_line_id.add_change_to_tracking()
        if view_type == 'tree':
            form_view_id = self.env['ir.model.data']._xmlid_to_res_id('sale_purchase_private'
                                                                      '.tracking_partner_consolide_list')
            if res.get('view_id') == form_view_id:
                if res['type'] == 'tree':
                    doc = etree.XML(res['arch'])
                    # raplace reference par correspondance
                    acq = doc.xpath("//field[@name='reference']")[0]
                    acq.attrib['name'] = 'correspondance'
                    acq.attrib['string'] = 'Référence'
                    xarch, xfields = self.env['ir.ui.view'].postprocess_and_fields(doc, model=self._name)

                    res['arch'] = xarch
                    res['fields'] = xfields
        return res

    def update_purchase_order(self):
        for line in self:
            purchase = self.env['purchase.order'].search([('name', '=', line.reference)])
            if purchase:
                line.purchase_id = purchase

    def printer_button(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.rapport',
            'views': [[self.env.ref('sale_purchase_private.rapport_purchase_form').id, 'form']],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'name': 'Rapport',
        }

    def update_vendor_partner_type(self):
        vendors = self.env['tracking.partner'].search([])
        for vendor in vendors:
            vendor.partner_type = 'vendor'