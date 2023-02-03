# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.main import DataSet
class SessionInherit(DataSet):

	@http.route(['/web/dataset/call_kw', '/web/dataset/call_kw/<path:path>'], type='json', auth="user")
	def call_kw(self, model, method, args, kwargs, path=None):
		print("Dans le call_kw *****************", model)
		# print("Method", method)
		# print("args", args)
		# if 'params' in kwargs['context'].keys():
			# kwargs['context']['params']['action'] = 353
			# for val in kwargs:
			# 	print("la val", val)
		# if model == 'sale.report':
		# 	print("Avant verif", kwargs)
		# 	if 'fields' in kwargs.keys():
		# 		kwargs['fields'] = ['price_subtotal:sum']
			# if 'fields' in kwargs.keys():
			# 	if 'price_total:sum' in kwargs['fields']:
			# 		kwargs['fields'] = ['price_subtotal:sum']
				# print("kwargs", kwargs['fields'])
		return self._call_kw(model, method, args, kwargs)


# class TestAddons/dashboard(http.Controller):
#     @http.route('/test_addons/dashboard/test_addons/dashboard', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/test_addons/dashboard/test_addons/dashboard/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('test_addons/dashboard.listing', {
#             'root': '/test_addons/dashboard/test_addons/dashboard',
#             'objects': http.request.env['test_addons/dashboard.test_addons/dashboard'].search([]),
#         })

#     @http.route('/test_addons/dashboard/test_addons/dashboard/objects/<model("test_addons/dashboard.test_addons/dashboard"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('test_addons/dashboard.object', {
#             'object': obj
#         })
