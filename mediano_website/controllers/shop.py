# -*- coding: utf-8 -*-
from odoo import http, tools, _
from odoo.addons.website_sale.controllers.main import WebsiteSale
# from odoo.addons.website_sale_delivery.controllers.main import WebsiteSaleDelivery
from odoo.http import request
import logging
import qrcode
import base64
from io import BytesIO
# from odoo.exceptions import UserError


from werkzeug.exceptions import Forbidden

_logger = logging.getLogger(__name__)


class WebsiteSaleInherit(WebsiteSale):

    def recover_price_from_shipping(self, order):
        """Récupération de l'ID du partner Actif"""
        if order.partner_shipping_id.city == 'Showroom':
            order.old_partner = order.partner_shipping_id
            # print('OOP', order.old_partner)
            """Recherche de la commune lié au partner"""
            commune = order.old_partner.commune_id.name
            # print('Commune', commune)
        else:
            order.new_partner = order.partner_shipping_id
            # print('ONP', order.new_partner)
            """Recherche de la commune lié au partner"""
            commune = order.new_partner.commune_id.name

        """Définition des variables de recherche"""
        carrier = order.carrier_id.sudo()
        product = carrier.product_id

        if commune:
            """Si la commune existe"""
            # print('Good Work')
            product_id = product.search([('default_code', '=', commune.lower())])
            carrier_id = carrier.search([('product_id', '=', product_id.id)])
            order.carrier_id = carrier_id
        else:
            """ Sinon frais 0 FCFA"""
            # print('Bad Work')
            carrier_id = carrier.search([('free_over', '=', True)])
            order.carrier_id = carrier_id

        # print('Carrier ID', order.carrier_id, 'Delivery Price', order.carrier_id.fixed_price)

    @http.route(['/shop/address'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def address(self, **kw):
        super(WebsiteSaleInherit, self).address(**kw)
        Partner = request.env['res.partner'].with_context(show_address=1).sudo()
        Commune = request.env['res.commune'].sudo()
        order = request.website.sale_get_order()

        redirection = self.checkout_redirection(order)
        if redirection:
            return redirection

        mode = (False, False)
        can_edit_vat = False
        values, errors = {}, {}

        """Récupère le partner adéquat"""
        partner_id = int(kw.get('partner_id', -1))

        # IF PUBLIC ORDER
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            mode = ('new', 'billing')
            can_edit_vat = True
        # IF ORDER LINKED TO A PARTNER
        else:
            if partner_id > 0:
                """Si l'id stocké dans la variable équivaut à celui de l'id parent :
                 Mode edition adresse de facturation"""
                if partner_id == order.partner_id.id:
                    mode = ('edit', 'billing')
                    print('partn', int(kw.get('partner_id')))
                    can_edit_vat = order.partner_id.can_edit_vat()
                    """Charger les valeurs du contact dont l'adresse est la facturation"""
                    print('CMZ', order.partner_id.commune_id.name)
                    print('CMZ', order.partner_id.plus_detail)

                    values = Partner.browse(order.partner_id.id)
                    print('Values', values.plus_detail)
                else:
                    """Sinon si l'id stocké dans la variable équivaut à celui de l'id parent :
                                     Mode edition adresse de facturation"""
                    shippings = Partner.search([('id', 'child_of', order.partner_id.commercial_partner_id.ids)])
                    print('Commercial', order.partner_id.commercial_partner_id.id)
                    print('partner_id', partner_id)
                    print('Sippings', shippings.mapped('id'))
                    if order.partner_id.commercial_partner_id.id == partner_id:
                        """Si l'id stocké dans la variable équivaut à l'id selectionnée"""
                        mode = ('new', 'shipping')
                        partner_id = -1
                        print('New shipping')
                        """Charger les valeurs du contact par défaut"""
                        # values = Partner.browse(int(kw.get('partner_id')))
                    elif partner_id in shippings.mapped('id'):
                        """Si l'id stocké dans la variable équivaut est dans la liste des adresses de livraisons"""
                        mode = ('edit', 'shipping')
                        values = Partner.browse(partner_id)
                        print('Vals #2', values)
                    else:
                        """Sinon retourné interdiction"""
                        return Forbidden()
                print('Mode', mode, 'partner', partner_id)
                if mode and partner_id != -1:
                    print('partner #', Partner.browse(partner_id))
                    values = Partner.browse(partner_id)
            elif partner_id == -1:
                """Charger la valeur de l'ID parent pour une nouvelle adresse de livraison"""
                mode = ('new', 'shipping')
                values = Partner.browse(order.partner_id.id)
                print('New shipping')
            else:  # no mode - refresh without post?
                return request.redirect('/shop/checkout')

        # IF POSTED
        if 'submitted' in kw and request.httprequest.method == "POST":

            print('Pt2', partner_id)
            """Récupération de la commune adéquate en fonction du partner_id"""
            com = Commune.search([('id', '=', int(kw.get('commune_id')))])
            print('Comm', com.name)
            print('Carrier_id', order.carrier_id)

            if not kw.get('country_id'):
                kw['country_id'] = 44
            if not kw.get('street'):
                kw['street'] = com.name
            if not kw.get('commune_id'):
                kw['commune_id'] = 1
            if not kw.get('city'):
                kw['city'] = kw.get('ville')
            if not kw.get('zip'):
                kw['zip'] = "00225"
            pre_values = self.values_preprocess(kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                partner_id = self._checkout_form_save(mode, post, kw)
                # We need to validate _checkout_form_save return, because when partner_id not in shippings
                # it returns Forbidden() instead the partner_id
                if isinstance(partner_id, Forbidden):
                    return partner_id
                if mode[1] == 'billing':
                    """Mise à jour des champs commune et détails pour l'adresse de facturation"""
                    print('Pt3', partner_id)
                    order.partner_id = partner_id
                    order.partner_id.commune_id = com
                    order.partner_id.plus_detail = kw.get('details')

                    # order.with_context(not_self_saleperson=True).onchange_partner_id()
                    # This is the *only* thing that the front end user will see/edit anyway when choosing billing address
                    order.partner_invoice_id = partner_id
                    print("Invoice Id", order.partner_invoice_id)
                    if not kw.get('use_same'):
                        kw['callback'] = kw.get('callback') or \
                                         (not order.only_services and (
                                                 mode[0] == 'edit' and '/shop/checkout' or '/shop/address'))
                    # We need to update the pricelist(by the one selected by the customer), because onchange_partner reset it
                    # We only need to update the pricelist when it is not redirected to /confirm_order
                    if kw.get('callback', '') != '/shop/confirm_order':
                        request.website.sale_get_order(update_pricelist=True)
                elif mode[1] == 'shipping':
                    """Mise à jour des champs commune et détails pour les adresses de livraison"""
                    print('Pt4', partner_id)
                    order.partner_shipping_id = partner_id
                    order.partner_shipping_id.commune_id = com
                    order.partner_shipping_id.plus_detail = kw.get('details')
                    # product_id = order.carrier_id.product_id.sudo().search([('default_code', '=', com.name.lower())])
                    # order.carrier_id = order.carrier_id.sudo().search([('product_id', '=', product_id.id)])
                    # print('Carrier_id #', order.carrier_id, 'Delivery Price', order.carrier_id.fixed_price)

                # TDE FIXME: don't ever do this
                # -> TDE: you are the guy that did what we should never do in commit e6f038a
                order.message_partner_ids = [(4, partner_id), (3, request.website.partner_id.id)]
                if not errors:
                    # return request.redirect(kw.get('callback') or '/shop/confirm_order')
                    print('redirection')
                    return request.redirect(kw.get('callback') or '/shop/checkout')

        communes = request.env['res.commune'].sudo().search([])
        print('Error', errors)

        render_values = {
            'website_sale_order': order,
            'partner_id': partner_id,
            'mode': mode,
            'communes': communes,
            'checkout': values,
            'can_edit_vat': can_edit_vat,
            'error': errors,
            'callback': kw.get('callback'),
            'only_services': order and order.only_services,
            'account_on_checkout': request.website.account_on_checkout,
            'is_public_user': request.website.is_public_user()
        }

        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("website_sale.address", render_values)

    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        super(WebsiteSaleInherit, self).checkout(**post)
        order = request.website.sale_get_order()

        """Fonction pour récuperer les frais de Livraisons"""
        self.recover_price_from_shipping(order)

        redirection = self.checkout_redirection(order)

        if redirection:
            return redirection

        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            return request.redirect('/shop/address')

        redirection = self.checkout_check_address(order)

        if redirection:
            return redirection

        values = self.checkout_values(**post)
        print('Values #5', values)

        if post.get('express'):
            return request.redirect('/shop/confirm_order')

        values.update({'website_sale_order': order})

        # Avoid useless rendering if called in ajax
        if post.get('xhr'):
            return 'ok'
        return request.render("website_sale.checkout", values)

    @http.route(['/shop/confirm_order'], type='http', auth="public", website=True, sitemap=False)
    def confirm_order(self, **post):
        super(WebsiteSaleInherit, self).confirm_order(**post)
        order = request.website.sale_get_order()
        print('Confirm Order Partner', order.old_partner)

        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        """Fonction pour récuperer les frais de Livraisons"""
        self.recover_price_from_shipping(order)

        order.order_line._compute_tax_id()
        request.session['sale_last_order_id'] = order.id
        request.website.sale_get_order(update_pricelist=True)
        extra_step = request.website.viewref('website_sale.extra_info_option')
        if extra_step.active:
            return request.redirect("/shop/extra_info")

        return request.redirect("/shop/payment")

    def _get_shop_payment_values(self, order, **kwargs):

        """Fonction pour récuperer les frais de Livraisons"""
        self.recover_price_from_shipping(order)

        values = super(WebsiteSaleInherit, self)._get_shop_payment_values(order, **kwargs)

        """Affectation du coût de livraison et calcul des frais et montant total"""
        values['order']['carrier_id'] = order.carrier_id
        values['deliveries'] = order.carrier_id
        values['amount_delivery'] = order.carrier_id.fixed_price

        return values

    @http.route('/shop/payment', type='http', auth='public', website=True, sitemap=False)
    def shop_payment(self, **post):
        """ Payment step. This page proposes several payment means based on available
        payment.acquirer. State at this point :

         - a draft sales order with lines; otherwise, clean context / session and
           back to the shop
         - no transaction in context / session, or only a draft one, if the customer
           did go to a payment.acquirer website but closed the tab without
           paying / canceling
        """
        super(WebsiteSaleInherit, self).shop_payment(**post)

        order = request.website.sale_get_order()
        redirection = self.checkout_redirection(order) or self.checkout_check_address(order)
        if redirection:
            return redirection

        render_values = self._get_shop_payment_values(order, **post)
        render_values['only_services'] = order and order.only_services or False

        if render_values['errors']:
            render_values.pop('providers', '')
            render_values.pop('tokens', '')

        return request.render("website_sale.payment", render_values)

    @http.route(['/shop/confirmation'], type='http', auth="public", website=True, sitemap=False)
    def shop_payment_confirmation(self, **post):
        super(WebsiteSaleInherit, self).shop_payment_confirmation(**post)
        sale_order_id = request.session.get('sale_last_order_id')
        if sale_order_id:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            values = self._prepare_shop_payment_confirmation_values(order)
            """Intégration du Qr Code"""
            values.update({'qr': self.generate_qr_code(order)})
            return request.render("website_sale.confirmation", values)
        else:
            return request.redirect('/shop')

    def generate_qr_code(self, order):
        """Fonction permettant de générer un Qr Code spécifique à la vente"""
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        access_token = order._portal_ensure_token()
        if not 'localhost' in base_url:
            if 'http://' in base_url:
                base_url = base_url.replace('http://', 'https://')
        base_url = base_url + '/my/orders/' + str(order.id) + '?access_token=' + str(access_token) + '&report_type=pdf'
        # base_url = base_url + '/my/orders/' + str(order.id)

        qr_code = qrcode.QRCode(version=4, box_size=4, border=1)
        qr_code.add_data(base_url)
        qr_code.make(fit=True)
        qr_img = qr_code.make_image()
        im = qr_img._img.convert("RGB")
        buffered = BytesIO()
        im.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('ascii')
        return img_str

    @http.route('/shop/payment/get_status/<int:sale_order_id>', type='json', auth="public", website=True)
    def shop_payment_get_status(self, sale_order_id, **post):
        super(WebsiteSaleInherit, self).shop_payment_get_status(sale_order_id, **post)
        order = request.env['sale.order'].sudo().browse(sale_order_id).exists()
        if order.id != request.session.get('sale_last_order_id'):
            # either something went wrong or the session is unbound
            # prevent recalling every 3rd of a second in the JS widget
            print('Return')
            # return {}

        return {
            'recall': order.get_portal_last_transaction().state == 'pending',
            'message': request.env['ir.ui.view']._render_template("website_sale.payment_confirmation_status", {
                'order': order,
                'qr': self.generate_qr_code(order)
            })
        }

    @http.route(['/shop/payment/delivery'], type='json', auth="user", website=True)
    def swap_delivery_fees(self, **post):
        order = request.website.sale_get_order()
        check = ''
        get_adl = post.get('adl')
        print('Get ADL', get_adl)

        """Rechercher des tous les ID lié au partner"""
        child = request.env['res.partner'].sudo().search(
            [('id', 'child_of', order.partner_id.commercial_partner_id.ids)])

        """Recherche de l'ID de Showroom"""
        for elt in child:
            if elt.street == 'Marcory Zone 4':
                check = elt

        # """Recherche de l'ID du partenaire"""
        # # checkit = request.env['res.partner'].sudo().search(
        # #     [('id', '=', order.partner_id.id), ('street', '=', order.partner_id.street)])
        if get_adl == 1:
            # print('Livraison Normale')
            # self.recover_price_from_shipping(order)
            order.partner_shipping_id = order.new_partner
            # print('OLD partner', order.partner_shipping_id)

            # if not order.old_partner:
            #     last_order = request.env['sale.order'].sudo().search(
            #         [('partner_id', '=', order.partner_shipping_id.id)])
            #     if len(last_order) >= 2:
            #         order.old_partner = last_order[-1].partner_shipping_id or last_order[-1].partner_id
            #     else:
            #         order.old_partner = order.partner_id
            # else:
            #     pass
            #
            # if parent == order.old_partner:
            #     order.partner_shipping_id = parent
            # else:
            #     order.partner_shipping_id = order.old_partner

            return 'adl'

        elif get_adl == 2:
            # print('Livraison Showroom')
            """Coordonnées pour la Livraison depuis le Showroom"""
            mode = ('new', 'shipping')
            kw = {'name': order.partner_id.name,
                  'email': order.partner_id.email,
                  'phone': order.partner_id.phone,
                  'city': 'Showroom',
                  'street': 'Marcory Zone 4',
                  'commune_id': None,
                  'is_showroom': True,
                  'country_id': 44,
                  'zip': '00225'}

            pre_values = self.values_preprocess(kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            """Recherche de l'ID correspondant à ShowRoom"""
            if check:
                print('existant')
                order.partner_shipping_id = check
                # self.recover_price_from_shipping(order)
            else:
                print('non existant')
                """Création du contact Showroom"""
                partner_id = self._checkout_form_save(mode, post, kw)
                # print('Partner Showroom', partner_id)
                order.partner_shipping_id = partner_id
                self.recover_price_from_shipping(order)

            return 'shwrm'