# -*- coding: utf-8 -*-
# from odoo import http


# class PosHideRefund(http.Controller):
#     @http.route('/pos_hide_refund/pos_hide_refund/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_hide_refund/pos_hide_refund/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_hide_refund.listing', {
#             'root': '/pos_hide_refund/pos_hide_refund',
#             'objects': http.request.env['pos_hide_refund.pos_hide_refund'].search([]),
#         })

#     @http.route('/pos_hide_refund/pos_hide_refund/objects/<model("pos_hide_refund.pos_hide_refund"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_hide_refund.object', {
#             'object': obj
#         })
