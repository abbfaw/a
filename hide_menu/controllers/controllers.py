# -*- coding: utf-8 -*-
# from odoo import http


# class HideMenu(http.Controller):
#     @http.route('/hide_menu/hide_menu', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hide_menu/hide_menu/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('hide_menu.listing', {
#             'root': '/hide_menu/hide_menu',
#             'objects': http.request.env['hide_menu.hide_menu'].search([]),
#         })

#     @http.route('/hide_menu/hide_menu/objects/<model("hide_menu.hide_menu"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hide_menu.object', {
#             'object': obj
#         })
