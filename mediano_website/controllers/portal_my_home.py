from odoo import http, tools, _
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.http import request
from odoo.addons.portal.controllers.portal import pager as portal_pager, get_records_pager


class CustomerPortalInherit(CustomerPortal):

    @http.route(['/my/account'], type='http', auth='user', website=True)
    def account(self, redirect=None, **post):
        values = self._prepare_portal_layout_values()
        partner = request.env.user.partner_id
        values.update({
            'error': {},
            'error_message': [],
        })

        if post and request.httprequest.method == 'POST':
            print("Post", post)
            if not post.get('street'):
                post['street'] = "Rue non renseignée"
            if not post.get('city'):
                post['city'] = "Ville non renseignée"
            if not post.get('zipcode'):
                post['zipcode'] = "00225"
            error, error_message = self.details_form_validate(post)
            values.update({'error': error, 'error_message': error_message})
            values.update(post)
            if not error:
                values = {key: post[key] for key in self.MANDATORY_BILLING_FIELDS}
                values.update({key: post[key] for key in self.OPTIONAL_BILLING_FIELDS if key in post})
                for field in set(['country_id', 'state_id']) & set(values.keys()):
                    try:
                        values[field] = int(values[field])
                    except:
                        values[field] = False
                values.update({'zip': values.pop('zipcode', '')})
                partner.sudo().write(values)
                if redirect:
                    return request.redirect(redirect)
                return request.redirect('/my/home')

        countries = request.env['res.country'].sudo().search([])
        states = request.env['res.country.state'].sudo().search([])

        values.update({
            'partner': partner,
            'countries': countries,
            'states': states,
            'has_check_vat': hasattr(request.env['res.partner'], 'check_vat'),
            'redirect': redirect,
            'page_name': 'my_details',
        })

        response = request.render("portal.portal_my_details", values)
        response.headers['X-Frame-Options'] = 'DENY'
        return response

    @http.route(['/commandes/effectuees', '/commandes/effectuees/page/<int:page>'], type='http', auth="user",
                website=True)
    def commande_effectuee(self, **kwargs):
        print("Commandes en cours de traitement", **kwargs)
        values = self._prepare_sale_portal_rendering_values(quotation_page=True, **kwargs)
        request.session['my_quotations_history'] = values['quotations'].ids[:100]

        return request.render("mediano_website.portail_commandes_en_cours", values)

    @http.route(['/commandes/validees', '/commandes/validees/page/<int:page>'], type='http', auth="user", website=True)
    def commande_validee(self, **kwargs):
        print("Commandes en traitées", **kwargs)
        values = self._prepare_sale_portal_rendering_values(quotation_page=False, **kwargs)
        request.session['my_orders_history'] = values['orders'].ids[:100]

        return request.render("mediano_website.portail_commandes_validees", values)

    @http.route(['/commandes/annulees', '/commandes/annulees/page/<int:page>'], type='http', auth="user", website=True)
    def commande_annulee(self, **kwargs):
        print("Commandes annulées", **kwargs)
        values = self._prepare_sale_cancel_portal_rendering_values(cancel_page=True, **kwargs)
        request.session['my_orders_history'] = values['cancels'].ids[:100]

        return request.render("mediano_website.portail_commandes_annulees", values)

    def _prepare_sale_portal_rendering_values(self, page=1, date_begin=None, date_end=None, sortby=None, quotation_page=False, **kwargs):
        super(CustomerPortalInherit, self)._prepare_sale_portal_rendering_values(page=1, date_begin=None, date_end=None,
                                                                                 sortby=None, quotation_page=False,
                                                                                 **kwargs)

        SaleOrder = request.env['sale.order'].sudo()

        if not sortby:
            sortby = 'date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        if quotation_page:
            url = "/commandes/effectuees"
            domain = self._prepare_quotations_domain(partner)
        else:
            url = "/commandes/validees"
            domain = self._prepare_orders_domain(partner)

        searchbar_sortings = self._get_sale_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=SaleOrder.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'quotations': orders.sudo() if quotation_page else SaleOrder,
            'orders': orders.sudo() if not quotation_page else SaleOrder,
            'page_name': 'commande_effectuee' if quotation_page else 'commande_validee',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    def _prepare_sale_cancel_portal_rendering_values(self, page=1, date_begin=None, date_end=None, sortby=None, cancel_page=False, **kwargs):

        SaleOrder = request.env['sale.order'].sudo()
        if not sortby:
            sortby = 'date'

        partner = request.env.user.partner_id
        values = self._prepare_portal_layout_values()

        if cancel_page:
            url = "/commandes/annulees"
            domain = self._prepare_cancel_domain(partner)
        else:
            url = "/commandes/annulees"
            domain = self._prepare_cancel_domain(partner)

        searchbar_sortings = self._get_sale_searchbar_sortings()

        sort_order = searchbar_sortings[sortby]['order']

        if date_begin and date_end:
            domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        pager_values = portal_pager(
            url=url,
            total=SaleOrder.search_count(domain),
            page=page,
            step=self._items_per_page,
            url_args={'date_begin': date_begin, 'date_end': date_end, 'sortby': sortby},
        )
        orders = SaleOrder.search(domain, order=sort_order, limit=self._items_per_page, offset=pager_values['offset'])

        values.update({
            'date': date_begin,
            'cancels': orders.sudo() if cancel_page else SaleOrder,
            'page_name': 'commande_annulee' if cancel_page else ' ',
            'pager': pager_values,
            'default_url': url,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
        })

        return values

    def _prepare_home_portal_values(self, counters):
        res = super(CustomerPortalInherit, self)._prepare_home_portal_values(counters)
        partner = request.env.user.partner_id

        SaleOrder = request.env['sale.order'].sudo()
        if 'quotation_count' in counters:
            res['quotation_count'] = SaleOrder.search_count(self._prepare_quotations_domain(partner)) \
                if SaleOrder.check_access_rights('read', raise_exception=False) else 0
        if 'order_count' in counters:
            res['order_count'] = SaleOrder.search_count(self._prepare_orders_domain(partner)) \
                if SaleOrder.check_access_rights('read', raise_exception=False) else 0

        if 'cancel_count' in counters:
            res['cancel_count'] = SaleOrder.search_count(self._prepare_cancel_domain(partner)) \
                if SaleOrder.check_access_rights('read', raise_exception=False) else 0

        return res

    def _prepare_quotations_domain(self, partner):
        super(CustomerPortalInherit, self)._prepare_quotations_domain(partner)
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', '=', 'sent')
        ]

    def _prepare_cancel_domain(self, partner):
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['cancel', 'done'])
        ]

    def _prepare_orders_domain(self, partner):
        super(CustomerPortalInherit, self)._prepare_orders_domain(partner)
        return [
            ('message_partner_ids', 'child_of', [partner.commercial_partner_id.id]),
            ('state', 'in', ['sale', 'done'])
        ]
