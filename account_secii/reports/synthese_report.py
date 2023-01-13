from odoo import models, api, fields

from datetime import date
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
        print('SD', start_date, 'TYPE', type(start_date))
        end_date = datetime.strptime(data.get('end_date'), '%d-%m-%Y')
        print('ED', end_date, 'TYPE', type(end_date))
        scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        name = scrap.name
        street = scrap.street
        date = datetime.now().strftime('%Y-%m-%d')
        payment = self.env['secii.encaissement']
        purchase = self.env['sale.order']
        retour = self.env['purchase.order']
        print('partner_id', partner_id)

        """"Recherche de toutes les ventes éffectuées entre les deux dates"""
        all_orders = purchase.search([('partner_id', '=', partner_id), ('state', 'in', ('sale', 'done')),
                                      ('date_effective', '>=', start_date),
                                      ('date_effective', '<=', end_date), ('is_prive', '=', 'True')])  # mettre create_date à la place de date_effective
        print('AO ->', all_orders)
        print('all ------ orders ..', all_orders)

        """Recherche de tous les encaissements éffectuéees entre les deux dates"""
        all_paie = payment.search(
            [('partenaire', '=', partner_id), ('status', 'in', ('paye', 'comptabilise')),
             ('date', '>=', start_date), ('date', '<=', end_date), ('instance', '=', 'True')])

        """Recherche de tous les retours éffectuéees entre les deux dates"""
        all_return = retour.search(
            [('partner_id', '=', partner_id), ('state', '=', 'purchase'),
             ('write_date', '>=', start_date), ('write_date', '<=', end_date), ('retour', '=', True)])
        print('All ----- Return', all_return)

        """Recherche des ventes ultérieurs aux dates sélectionnées"""
        past_purchase = sum(purchase.search([('partner_id', '=', partner_id),
                                             ('state', 'in', ('sale', 'done')),
                                             ('date_effective', '<', start_date), ('is_prive', '=', 'True')]).mapped('amount_total'))
        print('rest g...........', past_purchase)

        """Recherche des retours ultérieurs aux dates sélectionnées"""
        past_retour = sum(retour.search([('partner_id', '=', partner_id),
                                         ('state', '=', 'purchase'),
                                         ('retour', '=', True),
                                         ('write_date', '<', start_date)]).mapped('amount_total'))
        print('reste retour...........', past_retour)

        """Recherche des encaissements ultérieurs aux dates sélectionnées"""
        past_payment = sum(payment.search(
            [('partenaire', '=', partner_id),
             ('status', 'in', ('paye', 'comptabilise')),
             ('date', '<', start_date), ('instance', '=', 'True')]).mapped('somme_paye'))
        print('some   2222222222222222', past_payment)

        """Concaténation des dates selon create_date et write_date pour un éventuel tri"""
        all_date = all_orders.mapped('date_effective') + all_paie.mapped("write_date") + all_return.mapped("write_date")
        a = sorted(all_date)
        amount = (past_purchase - past_payment - past_retour)

        """Boucle permettant la recherche des dates de façon ordonnée ainsi que l'attribution et le calcul de données"""
        for x in a:
            all_vals = {}
            var = purchase.sudo().search(
                [("date_effective", '=', x), ('partner_id', '=', partner_id), ('is_prive', '=', 'True')])  # erreur si remplacer par date_effective
            var2 = payment.sudo().search([("write_date", '=', x), ('instance', '=', 'True')])
            var3 = retour.sudo().search([("write_date", '=', x), ('partner_id', '=', partner_id)])
            total_somme += var2.somme_paye
            for item in var:
                total_vente += item.amount_total
            for item in var3:
                total_retour += item.amount_total
            total_ant = past_purchase - past_payment
            total_final = total_vente + total_ant - total_somme - total_retour
            print('var', var)
            print('var2', var2)
            if var:
                all_vals.update({
                    'name': item.name,
                    'partner_id': item.partner_id.name,
                    'user_id': item.user_id.name,
                    'amount_total': item.amount_total,
                    'debit': item.amount_total,
                    'credit': 0,
                    'somme_paye': 0,
                    'solde': amount + item.amount_total,
                    'designation': 'BL-' + str(item.name),
                    'numero_bon': item.numero_bon,
                    'create_date': item.date_effective.strftime('%d-%m-%Y')
                })
                tbl.append(item.name)
                all_data.append(all_vals)
                amount += item.amount_total
            elif var2:
                all_vals.update({
                    'name': var2.num_seq,
                    'partner_id': var2.partenaire.name,
                    'user_id': var2.commercial.name,
                    'amount_total': var2.montant_total,
                    'debit': 0,
                    'credit': var2.somme_paye,
                    'somme_paye': var2.somme_paye,
                    'solde': int(amount - var2.somme_paye),
                    'designation': str(var2.num_seq),
                    'numero_bon': '',
                    'create_date': var2.write_date.strftime('%d-%m-%Y'),
                })
                tbl.append(var2.num_seq)
                all_data.append(all_vals)
                amount -= var2.somme_paye
            elif var3:
                all_vals.update({
                    'name': item.name,
                    'partner_id': item.partner_id.name,
                    'user_id': item.user_id.name,
                    'amount_total': item.amount_total,
                    'debit': 0,
                    'credit': item.amount_total,
                    'somme_paye': 0,
                    'solde': int(amount - item.amount_total),
                    'designation': 'RETOUR',
                    'numero_bon': '',
                    'create_date': item.write_date.strftime('%d-%m-%Y')
                })
                tbl.append(var3.name)
                all_data.append(all_vals)
                amount -= item.amount_total
        print('Tbl ===>', tbl)
        print('all_vals =>', all_vals)
        print('ADS =>', a)
        print('all pai', all_paie)
        print('all pai self ', self)
        print('all_data ', all_data)

        """Données renvoyées pour la création du Rapport"""
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
