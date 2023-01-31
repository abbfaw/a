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
        print('tu es mt 07571.........10861', data)
        partner_id = data.get('client')
        start_date = datetime.strptime(data.get('start_date'), '%d-%m-%Y')
        end_date = datetime.strptime(data.get('end_date'), '%d-%m-%Y')
        scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        name = scrap.name
        street = scrap.street
        date = datetime.now().strftime('%Y-%m-%d')
        payment = self.env['secii.enc'].sudo()
        purchase = self.env['secii.vente'].sudo()
        retour = self.env['purchase.order'].sudo()
        print('partner_id', partner_id)
        all_orders = purchase.search([('partner_id', '=', partner_id), ('date_order', '>=', start_date),('date_order', '<=', end_date)])
        print('all ------ orders ..', all_orders)
        all_paie = payment.search(
            [('partenaire', '=', partner_id), ('status', '=', 'paye'),
             ('create_date', '>=', start_date), ('create_date', '<=', end_date)])

        all_return = retour.search(
            [('partner_id', '=', partner_id), ('state', '=', 'purchase'),
             ('write_date', '>=', start_date), ('write_date', '<=', end_date), ('retour', '=', True), ('is_prive', '=', True)])

        past_purchase = sum(purchase.search([('partner_id', '=', partner_id),
                                             ('date_order', '<', start_date)]).mapped('amount_total'))
        print('rest g...........', past_purchase)
        past_payment = sum(payment.search(
            [('partenaire', '=', partner_id),
             ('status', '=', 'paye'),
             ('date', '<', start_date)]).mapped('somme_paye'))
        print('some   2222222222222222', past_payment)
        past_retour = sum(retour.search([('partner_id', '=', partner_id),
                                         ('state', '=', 'purchase'),
                                         ('retour', '=', True),
                                         ('is_prive', '=', True),
                                         ('write_date', '<', start_date)]).mapped('amount_total'))
        print('reste retour...........', past_retour)

        all_date = all_orders.mapped('create_date') + all_paie.mapped("create_date") + all_return.mapped("write_date")
        a = sorted(all_date)
        amount = (past_purchase - past_payment - past_retour)
        for x in a:
            print('A', len(a))
            all_vals = {}

            var = purchase.search(
                [("date_order", '=', x), ('partner_id', '=', partner_id)])
            var2 = payment.search(
                [("create_date", '=', x), ('partenaire', '=', partner_id)])
            print('var2', var2)
            var3 = retour.search([("write_date", '=', x), ('partner_id', '=', partner_id), ('retour', '=', True), ('is_prive', '=', True)])
            print('Somme Payee', var2.mapped('somme_paye'))
            total_ant = past_purchase - past_payment
            print('var', var)

            for order in var:
                if order.name not in tbl:
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
                        'numero_bon': order.numero_bon or ' ',
                        'create_date': order.date_order.strftime('%d-%m-%Y')
                    })
                    total_vente += order.amount_total
                    tbl.append(order.name)
                    all_data.append(all_vals)
                    print()
                    print('All Data #1', all_data)
                    print()
                    amount += order.amount_total
                    all_vals = {}
            for enc in var2:
                if enc.num_seq not in tbl:
                    print('ENCAISSEMENT', len(var2))
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
                        'create_date': enc.create_date.strftime('%d-%m-%Y'),
                    })
                    total_somme += enc.somme_paye
                    tbl.append(enc.num_seq)
                    all_data.append(all_vals)
                    print()
                    print('All Data #2', all_data)
                    print()
                    amount -= enc.somme_paye
                    all_vals = {}
            for ret in var3:
                if ret.name not in tbl:
                    print('RETOUR', len(var3))
                    all_vals.update({
                        'name': ret.name,
                        'partner_id': ret.partner_id.name,
                        'user_id': ret.user_id.name,
                        'amount_total': ret.amount_total,
                        'debit': 0,
                        'credit': ret.amount_total,
                        'libele': ' ',
                        'somme_paye': 0,
                        'solde': amount - ret.amount_total,
                        'designation': 'RETOUR',
                        'numero_bon': ' ',
                        'create_date': ret.write_date.strftime('%d-%m-%Y'),
                    })
                    total_retour += ret.amount_total
                    tbl.append(ret.name)
                    all_data.append(all_vals)
                    print()
                    print('All Data #3', all_data)
                    print()
                    amount -= ret.amount_total
                    all_vals = {}
            total_final = total_vente + total_ant - total_somme - total_retour
        print('all_vals =>', all_vals)
        print('Tbl ===>', tbl)
        print('all_data ', all_data)
        synthese = self.env['secii.synthese'].search([('id', '=', data.get('id'))])
        print('Reste :', synthese.reste, 'Type :', type(synthese.reste), 'ID :', synthese.id)
        credit_client = 0
        if synthese.reste < 0:
            credit_client = synthese.reste
        return {
            'docs': synthese,
            'all_orders': all_orders,
            'all_paie': all_paie,
            'all_data': all_data,
            'amount': amount,
            'credit_client': credit_client,
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
