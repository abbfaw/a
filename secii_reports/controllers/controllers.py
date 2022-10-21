# -*- coding: utf-8 -*-
# from odoo import http


# class CogebatReports(http.Controller):
#     @http.route('/cogebat_reports/cogebat_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/cogebat_reports/cogebat_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('cogebat_reports.listing', {
#             'root': '/cogebat_reports/cogebat_reports',
#             'objects': http.request.env['cogebat_reports.cogebat_reports'].search([]),
#         })

#     @http.route('/cogebat_reports/cogebat_reports/objects/<model("cogebat_reports.cogebat_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('cogebat_reports.object', {
#             'object': obj
#         })
