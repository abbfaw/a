# -*- coding: utf-8 -*-
# from odoo import http


# class PosDashboard(http.Controller):
#     @http.route('/pos_dashboard/pos_dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_dashboard/pos_dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_dashboard.listing', {
#             'root': '/pos_dashboard/pos_dashboard',
#             'objects': http.request.env['pos_dashboard.pos_dashboard'].search([]),
#         })

#     @http.route('/pos_dashboard/pos_dashboard/objects/<model("pos_dashboard.pos_dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_dashboard.object', {
#             'object': obj
#         })
