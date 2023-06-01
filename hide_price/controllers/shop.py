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
            carrier_id = carrier.search([('free_over', '=', True)])
            order.carrier_id = carrier_id

    def _get_shop_payment_values(self, order, **kwargs):

        """Fonction pour récuperer les frais de Livraisons"""
        self.recover_price_from_shipping(order)

        values = super(WebsiteSaleInherit, self)._get_shop_payment_values(order, **kwargs)

        """Affectation du coût de livraison et calcul des frais et montant total"""
        values['order']['carrier_id'] = order.carrier_id
        values['deliveries'] = order.carrier_id
        values['amount_delivery'] = order.carrier_id.fixed_price

        return values

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

    @http.route(['/shop/quotation'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def quotation(self, **kw):
        communes = request.env['res.commune'].sudo().search([])
        order = request.website.sale_get_order()

        mode = (False, False)
        values, errors = {}, {}

        if 'submitted' in kw and request.httprequest.method == "POST":
            """Récupération des infos"""

            mode = ('new', 'billing')
            kw = {'name': kw.get('name'),
                  'email': kw.get('email'),
                  'phone': kw.get('phone'),
                  'city': kw.get('city'),
                  'street': ' ',
                  'commune_id': kw.get('commune_id'),
                  'visitors': True,
                  'country_id': 44,
                  'zip': '00225'}

            pre_values = self.values_preprocess(kw)
            errors, error_msg = self.checkout_form_validate(mode, kw, pre_values)
            post, errors, error_msg = self.values_postprocess(order, mode, pre_values, errors, error_msg)

            if errors:
                errors['error_message'] = error_msg
                values = kw
            else:
                user = request.env['res.partner'].sudo().search(
                    [('email', '=', kw.get('email')), ('phone', '=', kw.get('phone'))])

                if user:
                    order.partner_id = user.id
                    category_id = request.env['crm.tag'].sudo().search([('color', '=', 9)])
                    if category_id:
                        order.tag_ids = category_id
                    """Redirection vers la page de quotation"""
                    return request.redirect('/shop/quotation_page')

                else:
                    """Si pas d'erreur créer le contact"""
                    partner_id = self._checkout_form_save(mode, post, kw)
                    print('P_ID', partner_id)
                    order.partner_id = partner_id

                    """Recherche de la category crée"""
                    category_id = request.env['res.partner.category'].sudo().search([('color', '=', 9)])

                    """vérification et attribution de l'étiquette aux visisteurs"""
                    if category_id:
                        order.partner_id.category_id = category_id

                    print('P_II', order.partner_id.name)
                    """Redirection vers la page de quotation"""
                    return request.redirect('/shop/quotation_page')

            print('Error', errors)

        render_values = {
            'website_sale_order': order,
            'mode': mode,
            # 'partner_id': partner_id,
            'communes': communes,
            'checkout': values,
            'error': errors,
            'only_services': order and order.only_services,
            'account_on_checkout': request.website.account_on_checkout,
            'is_public_user': request.website.is_public_user()
        }

        render_values.update(self._get_country_related_render_values(kw, render_values))
        return request.render("hide_price.address2", render_values)

    @http.route(['/shop/quotation_page'], type='http', auth="public", website=True, sitemap=False)
    def quotation_page(self, **post):
        order = request.website.sale_get_order()
        """les utilisateurs connectés ne peuvent voir cette page"""
        if not request.website.is_public_user():
            return request.redirect('/shop')
        else:
            # permts de vider le panier
            request.website.sale_reset()

        response = request.render('hide_price.quotation_message')
        response.headers['X-Frame-Options'] = 'DENY'
        return response
