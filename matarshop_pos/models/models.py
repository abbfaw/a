# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

from odoo.exceptions import UserError


class InheritPosOrder(models.Model):
    _inherit = 'pos.order'
    _order = 'date_order desc'

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        if not orderby and groupby:
            orderby_list = [groupby] if isinstance(groupby, str) else groupby
            orderby_list = [field.split(':')[0] for field in orderby_list]
            orderby = ','.join([f"{field} desc" if field == 'date_order' else field for field in orderby_list])
        return super().read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)


class InheritPosSession(models.Model):
    _inherit = 'pos.session'

    amount_expected = fields.Monetary(string='Expected amount', compute='_compute_amount_expected')
    cash_number = fields.Integer(string='Enter/exit', compute='_compute_amount_expected')
    cash_in_out = fields.Monetary(string='Total cash in/out', compute='_compute_amount_expected')
    amount_orders_total = fields.Monetary(string='Order amount', compute='_compute_amount_expected')
    amount_bank = fields.Monetary(string='bank orders', compute='_compute_amount_expected')
    amount_cash = fields.Monetary(string='cash orders', compute='_compute_amount_expected')
    cash_label = fields.Char()
    symbol_devise = fields.Char(string='symbol',related="company_id.currency_id.symbol",searchable= True)
    

    @api.model
    def check_user_access(self):
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('point_of_sale.group_pos_manager'):
            return True
        else:
            return False

    def get_closing_control_data(self):
        no_access = False
        data = super(InheritPosSession, self).get_closing_control_data()
        res_user = self.env['res.users'].search([('id', '=', self._uid)])
        if res_user.has_group('pos_delete_orderline.group_pos_reponsable_user') and res_user.has_group('point_of_sale.group_pos_manager'):
            no_access = False
        elif res_user.has_group('pos_delete_orderline.group_pos_reponsable_user'):
            no_access = True
        else: 
            no_access = False
        data['default_cash_details'].update({'no_access': no_access})
        return data

    def try_cash_in_out(self, _type, amount, reason, comment, extras):
        sign = 1 if _type == 'in' else -1
        sessions = self.filtered('cash_journal_id')
        if not sessions:
            raise UserError(_("There is no cash payment method for this PoS Session"))

        self.env['account.bank.statement.line'].create([
            {
                'pos_session_id': session.id,
                'journal_id': session.cash_journal_id.id,
                'amount': sign * amount,
                'comment': comment,
                'date': fields.Date.context_today(self),
                'payment_ref': '-'.join([session.name, extras['translatedType'], reason]),
            }
            for session in sessions
        ])

        message_content = [f"Cash {extras['translatedType']}", f'- Amount: {extras["formattedAmount"]}']
        if reason:
            message_content.append(f'- Reason: {reason}')
        self.message_post(body='<br/>\n'.join(message_content))

    def _compute_amount_expected(self):
        for record in self:
            orders = record.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
            payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
            last_session = record.search([('config_id', '=', record.config_id.id), ('id', '!=', record.id)], limit=1)
            cash_payment_method_ids = record.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
            default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
            total_default_cash_payment_amount = sum(
                payments.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped(
                    'amount')) if default_cash_payment_method_id else 0
            other_payment_method_ids = record.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else record.payment_method_ids

            other_amount = 0
            cash_amount = 0
            other_payment = self.env['pos.payment'].search([('session_id', '=', record.id)])
            # cash_payment = self.env['pos.payment'].search([('session_id', '=', record.id)])
            for rec in other_payment:
                if rec.payment_method_id.journal_id.type == 'bank':
                    other_amount += rec.amount
                elif rec.payment_method_id.journal_id.type == 'cash':
                    cash_amount += rec.amount
                    print(cash_amount)
            print(cash_amount)      
            record.amount_bank = other_amount
            record.amount_cash = cash_amount
            record.amount_expected = last_session.cash_register_balance_end_real + total_default_cash_payment_amount + sum(record.statement_line_ids.mapped('amount'))
            record.cash_number = len(record.statement_line_ids)
            record.amount_orders_total = record.total_payments_amount
            statement_line_ids = self.statement_line_ids.sorted('create_date')
            if statement_line_ids:
                for cash_move in statement_line_ids:
                    record.cash_in_out += cash_move.amount
            else:
                record.cash_in_out = 0

    def open_cash_in_out(self):

        cash_in_count = 0
        cash_out_count = 0
        cash_in_out_list = []
        for cash_move in self.statement_line_ids.sorted('create_date'):
            if cash_move.amount > 0:
                cash_in_count += 1
                name = f'Cash in {cash_in_count}'
            else:
                cash_out_count += 1
                name = f'Cash out {cash_out_count}'
            cash_in_out_list.append({
                'name': cash_move.payment_ref if cash_move.payment_ref else name,
                'amount': cash_move.amount,
                'cash_type': name,
            })
        self.env['cash.in.out'].sudo().search([]).unlink()
        self.env['cash.in.out'].create(cash_in_out_list)
        return {
            'name': _('Entree/sortie'),
            'view_mode': 'tree',
            'res_model': 'cash.in.out',
            'view_id': self.env.ref('matarshop_pos.view_cash_in_out_tree').id,
            'target': 'new',
            'type': 'ir.actions.act_window',
            'context': self.env.context,
        }

    def open_payment_method(self):

        # for pm in other_payment_method_ids:
        #     print('type ........', pm.type)
        #     print('type ........', pm.name)
        #     print('type ........len', len(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm)))
        #     print('test bonjour .......',
        #           sum(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm).mapped('amount')))

        orders = self.order_ids.filtered(lambda o: o.state == 'paid' or o.state == 'invoiced')
        cash_payment_method_ids = self.payment_method_ids.filtered(lambda pm: pm.type == 'cash')
        default_cash_payment_method_id = cash_payment_method_ids[0] if cash_payment_method_ids else None
        other_payment_method_ids = self.payment_method_ids - default_cash_payment_method_id if default_cash_payment_method_id else self.payment_method_ids
        last_session = self.search([('config_id', '=', self.config_id.id), ('id', '!=', self.id)], limit=1)
        payments = orders.payment_ids.filtered(lambda p: p.payment_method_id.type != "pay_later")
        total_default_cash_payment_amount = sum(
            payments.filtered(lambda p: p.payment_method_id == default_cash_payment_method_id).mapped(
                'amount')) if default_cash_payment_method_id else 0
        other_payment_methods = [{
            'name': pm.name,
            'amount': sum(orders.payment_ids.filtered(lambda p: p.payment_method_id == pm).mapped('amount')),
        } for pm in other_payment_method_ids]

        other_payment_methods.append({'name': default_cash_payment_method_id.name,
                                      'amount': last_session.cash_register_balance_end_real
                                                + total_default_cash_payment_amount
                                                + sum(self.statement_line_ids.mapped('amount')), })
        self.env['payment.method'].search([]).unlink()
        self.env['payment.method'].create(other_payment_methods)

        return {
            'name': _('Methodes de paiements'),
            'view_mode': 'tree',
            'res_model': 'payment.method',
            'view_id': False,
            'target': 'new',
            'views': False,
            'type': 'ir.actions.act_window',
            'context': self.env.context,
        }


class inheritAccountMove(models.Model):
    _inherit='account.bank.statement.line'

    comment = fields.Char(string='Description')
