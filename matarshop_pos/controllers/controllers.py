# -*- coding: utf-8 -*-
# from odoo import http


# class MatarshopPos(http.Controller):
#     @http.route('/matarshop_pos/matarshop_pos', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/matarshop_pos/matarshop_pos/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('matarshop_pos.listing', {
#             'root': '/matarshop_pos/matarshop_pos',
#             'objects': http.request.env['matarshop_pos.matarshop_pos'].search([]),
#         })

#     @http.route('/matarshop_pos/matarshop_pos/objects/<model("matarshop_pos.matarshop_pos"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('matarshop_pos.object', {
#             'object': obj
#         })
