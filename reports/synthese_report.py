from odoo import models, api, fields
from datetime import datetime
import pytz


class ProjectReportParser(models.AbstractModel):
    _name = 'report.account_secii.report_synthese_partner_view'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    @api.model
    def _get_report_values(self, docids, data=None):
        global var2
        all_vals = {}
        tbl = []
        all_data = []
        amount = 0
        total_somme = 0
        total_vente = 0
        total_retour = 0
        total_final = 0
        total_ant = 0
        print('tu es mt 01233.........885520', data)
        partner_id = data.get('client')
        start_date = datetime.strptime(data.get('start_date'), '%d-%m-%Y')
        end_date = datetime.strptime(data.get('end_date'), '%d-%m-%Y')
        scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        name = scrap.name
        street = scrap.street
        date = datetime.now().strftime('%Y-%m-%d')
        payment = self.env['secii.encaissement'].sudo()
        purchase = self.env['sale.order'].sudo()
        retour = self.env['purchase.order'].sudo()
        print('partner_id', partner_id)
        all_orders = purchase.search([('partner_id', '=', partner_id), ('state', 'in', ('sale', 'done')),
                                      ('date_effective', '>=', start_date),
                                      ('date_effective', '<=', end_date), ('is_prive', '=', True)])
        print('all ------ orders ..', all_orders)
        all_paie = payment.search(
            [('partenaire', '=', partner_id), ('status', 'in', ('paye', 'comptabilise')),
             ('date', '>=', start_date), ('date', '<=', end_date), ('instance', '=', True)])

        all_return = retour.search(
            [('partner_id', '=', partner_id), ('state', '=', 'purchase'),
             ('write_date', '>=', start_date), ('write_date', '<=', end_date), ('retour', '=', True)])

        past_purchase = sum(purchase.search([('partner_id', '=', partner_id),
                                             ('state', 'in', ('sale', 'done')),
                                             ('date_effective', '<', start_date),
                                             ('is_prive', '=', True)]).mapped('amount_total'))
        print('rest g...........', past_purchase)
        past_payment = sum(payment.search(
            [('partenaire', '=', partner_id),
             ('status', 'in', ('paye', 'comptabilise')),
             ('date', '<', start_date), ('instance', '=', True)]).mapped('somme_paye'))
        print('some   2222222222222222', past_payment)
        past_retour = sum(retour.search([('partner_id', '=', partner_id),
                                         ('state', '=', 'purchase'),
                                         ('retour', '=', True),
                                         ('is_prive', '=', True),
                                         ('write_date', '<', start_date)]).mapped('amount_total'))
        print('reste retour...........', past_retour)

        all_date = all_orders.mapped('date_effective') + all_paie.mapped("write_date") + all_return.mapped("write_date")
        a = sorted(all_date)
        amount = (past_purchase - past_payment - past_retour)
        for x in a:
            all_vals = {}
            var = purchase.search(
                [("date_effective", '=', x), ('partner_id', '=', partner_id), ('is_prive', '=', True)])
            var2 = payment.search(
                [("write_date", '=', x), ('partenaire', '=', partner_id), ('instance', '=', True)])
            var3 = retour.search([("write_date", '=', x), ('partner_id', '=', partner_id), ('retour', '=', True),
                                  ('is_prive', '=', True)])
            total_somme = sum(var2.mapped('somme_paye'))
            total_vente = sum(var.mapped('amount_total'))
            total_retour = sum(var3.mapped('amount_total'))
            total_ant = past_purchase - past_payment
            total_final = total_vente + total_ant - total_somme - total_retour
            print('var', var)
            print('var2', var2)
            for order in var:
                all_vals.update({
                    'name': order.name,
                    'partner_id': order.partner_id.name,
                    'user_id': order.user_id.name,
                    'amount_total': order.amount_total,
                    'debit': order.amount_total,
                    'credit': 0,
                    'libele': ' ',
                    'somme_paye': 0,
                    'solde': amount + order.amount_total,
                    'designation': 'BL-' + str(order.name),
                    'numero_bon': order.numero_bon,
                    'create_date': order.date_effective.strftime('%Y-%m-%d')
                })
                print('All vals ', all_vals)
                tbl.append(order.name)
                all_data.append(all_vals)
                print('all data de '+ order.name, all_data)
                amount += order.amount_total
            for enc in var2:
                all_vals.update({
                    'name': enc.num_seq,
                    'partner_id': enc.partenaire.name,
                    'user_id': enc.commercial.name,
                    'amount_total': enc.montant_total,
                    'debit': 0,
                    'credit': enc.somme_paye,
                    'libele': enc.libele_op,
                    'somme_paye': enc.somme_paye,
                    'solde': amount - enc.somme_paye,
                    'designation': str(enc.num_seq),
                    'numero_bon': ' ',
                    'create_date': enc.date,
                })
                tbl.append(enc.num_seq)
                all_data.append(all_vals)
                amount -= enc.somme_paye
            for ret in var3:
                all_vals.update({
                    'name': ret.num_seq,
                    'partner_id': ret.partenaire.name,
                    'user_id': ret.commercial.name,
                    'amount_total': ret.montant_total,
                    'debit': 0,
                    'credit': ret.somme_paye,
                    'libele': ' ',
                    'somme_paye': ret.somme_paye,
                    'solde': amount - ret.somme_paye,
                    'designation': str(ret.num_seq),
                    'numero_bon': ' ',
                    'create_date': ret.date,
                })
                tbl.append(ret.num_seq)
                all_data.append(all_vals)
                amount -= ret.somme_paye
        print('all_vals =>', all_vals)
        print('Tbl ===>', tbl)
        print('all_vals =>', all_vals)
        print('ADS =>', a)
        print('all pai', all_paie)
        print('all pai self ', self)
        print('all_data ', all_data)
        return {
            'docs': self.env['secii.synthese'].search([('id', '=', data.get('id'))]),
            'all_orders': all_orders,
            'all_paie': all_paie,
            'all_data': all_data,
            'amount': amount,
            'credit_client': var2.credit_client,
            'start_date': start_date,
            'end_date': end_date,
            'total_somme': total_somme + total_retour,
            'total_vente': total_vente + total_ant,
            'total_final': total_final,
            'total_ant': total_ant,
            'name': name,
            'street': street,
            'date': date,
        }
