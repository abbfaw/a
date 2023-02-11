import time
from ast import literal_eval

from odoo import models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class InheritStockPicking(models.Model):
    _inherit = 'stock.picking.type'

    @api.model
    def _compute_picking_count(self):
        print('redefinie ...............')
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        domains = {
            'count_picking_draft': [('state', '=', 'draft')],
            'count_picking_waiting': [('state', 'in', ('confirmed', 'waiting'))],
            'count_picking_ready': [('state', '=', 'assigned')],
            'count_picking': [('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_late': [('scheduled_date', '<', time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)),
                                   ('state', 'in', ('assigned', 'waiting', 'confirmed'))],
            'count_picking_backorders': [('backorder_id', '!=', False),
                                         ('state', 'in', ('confirmed', 'assigned', 'waiting'))],
        }
        for field in domains:
            if res_user.has_group('account_secii.sale_secii_users'):
                data = self.env['stock.picking'].read_group(domains[field] +
                                                            [('state', 'not in', ('done', 'cancel')),
                                                             ('picking_type_id', 'in', self.ids),
                                                             ('is_prive', '=', False)],
                                                            ['picking_type_id'], ['picking_type_id'])
                count = {
                    x['picking_type_id'][0]: x['picking_type_id_count']
                    for x in data if x['picking_type_id']
                }
                for record in self:
                    record[field] = count.get(record.id, 0)
            else:
                data = self.env['stock.picking'].read_group(domains[field] +
                                                            [('state', 'not in', ('done', 'cancel')),
                                                             ('picking_type_id', 'in', self.ids)],
                                                            ['picking_type_id'], ['picking_type_id'])
                count = {
                    x['picking_type_id'][0]: x['picking_type_id_count']
                    for x in data if x['picking_type_id']
                }
                for record in self:
                    record[field] = count.get(record.id, 0)

    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if self:
            action['display_name'] = self.display_name

        default_immediate_tranfer = True
        if self.env['ir.config_parameter'].sudo().get_param('stock.no_default_immediate_tranfer'):
            default_immediate_tranfer = False

        context = {
            'search_default_picking_type_id': [self.id],
            'default_picking_type_id': self.id,
            'default_immediate_transfer': default_immediate_tranfer,
            'default_company_id': self.company_id.id,
        }

        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        if res_user.has_group('account_secii.sale_secii_users'):
            action.update({'domain': [
                ('is_prive', '=', False)
            ]
            })
        action['context'] = context
        return action

    def get_stock_picking_action_picking_type(self):

        return self._get_action('stock.stock_picking_action_picking_type')

    def get_action_picking_tree_late(self):
        return self._get_action('stock.action_picking_tree_late')

    def get_action_picking_tree_backorder(self):
        return self._get_action('stock.action_picking_tree_backorder')

    def get_action_picking_tree_waiting(self):
        return self._get_action('stock.action_picking_tree_waiting')

    def get_action_picking_tree_ready(self):
        return self._get_action('stock.action_picking_tree_ready')

    def get_action_picking_type_operations(self):
        return self._get_action('stock.action_get_picking_type_operations')
