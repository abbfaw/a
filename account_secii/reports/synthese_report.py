from odoo import models, api, fields
from datetime import datetime
import pytz


class ProjectReportParser(models.AbstractModel):
    _name = 'report.account_secii.report_synthese_partner_view'

    def _default_time_utc(self):
        locale_time = datetime.now()
        dt_utc = locale_time.astimezone(pytz.UTC)
        return dt_utc

    # def sorted_list(self, list_to_sorted):
    #     split_up = list_to_sorted.split('-')
    #     print('Year', split_up[2], 'Month', split_up[1], 'Day', split_up[0])
    #     return split_up[2], split_up[1], split_up[0]

    @api.model
    def _get_report_values(self, docids, data=None):
        all_vals = {}
        tbl = []
        all_data = []
        amount = 0
        print('tu es mt 07571.........10861', data)
        partner_id = data.get('partner')
        start_date = datetime.strptime(data.get('start_date'), '%d-%m-%Y')
        end_date = datetime.strptime(data.get('end_date'), '%d-%m-%Y')
        scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        name = scrap.name
        street = scrap.street
        Date = datetime.now().strftime('%Y-%m-%d')
        tracking = self.env['tracking.partner'].sudo()
        print('partner_id', partner_id)

        """Recherche dans la table Tracking partner"""
        new_search = self.env['tracking.partner'].sudo().search(
            [('partner', '=', partner_id), ('date', '>=', start_date), ('date', '<=', end_date)], order='date asc')

        """ Recherche de tous ce qui est passés """
        past_amount_currency = sum(tracking.search(
            [('partner', '=', partner_id), ('date', '<', start_date), ('partner_type', '=', 'customer')]).mapped(
            'amount_currency'))
        print('PAST AMount', past_amount_currency)

        total_amount_currency = sum(tracking.search(
            [('partner', '=', partner_id), ('date', '>=', start_date), ('date', '<=', end_date),
             ('partner_type', '=', 'customer')]).mapped(
            'amount_currency'))
        print('Total AMount', total_amount_currency)

        amount = past_amount_currency
        # print('Tracking ------ orders ..', tracking_orders)
        for elt in new_search:
            """Pièces comptables +"""
            if elt.designation == 'Pièces comptables':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    'designation': 'SOLDE INITIAL',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.purchase_ref)
                all_data.append(all_vals)
                print()
                print('All Data #0', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Ventes +"""
            if elt.designation == 'Vente':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': elt.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': 'BL-' + str(elt.reference),
                    'designation': 'VENTE',
                    'libele_op': elt.libele_op or ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.purchase_ref)
                all_data.append(all_vals)
                print()
                print('All Data #1', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Achats +"""
            if elt.designation == 'Retour Achat':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': 0,
                    'credit': elt.amount_currency,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': 'BL-' + str(elt.reference),
                    'designation': "RETOUR D'ACHAT",
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.purchase_ref)
                all_data.append(all_vals)
                print()
                print('All Data #2', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Factures +"""
            if elt.designation == 'Facture Vente':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': str(elt.reference),
                    'designation': 'FACTURE',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                all_data.append(all_vals)
                print()
                print('All Data #3', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            if elt.designation == 'Avoir Client':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': elt.amount_currency,
                    'credit': 0,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': str(elt.reference),
                    'designation': 'FACTURE',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                all_data.append(all_vals)
                print()
                print('All Data #3', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Paiements -"""
            if elt.designation == 'Paiement':
                all_vals.update({
                    'name': elt.reference,
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': 0,
                    'credit': elt.amount_currency,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': str(elt.reference),
                    'designation': 'PAIEMENT',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                print('TBL PAIEMENT', tbl)
                all_data.append(all_vals)
                print()
                print('All Data #4', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

            """Encaissements -"""
            if elt.designation == 'Encaissement':
                all_vals.update({
                    'name': elt.reference or ' ',
                    'partner_id': elt.partner.name,
                    # 'user_id': tracking_orders.user_id.name,
                    'amount_total': elt.amount_currency,
                    'debit': 0,
                    'credit': elt.amount_currency,
                    'libele': elt.libele_op or ' ',
                    'somme_paye': 0,
                    'solde': amount + elt.amount_currency,
                    # 'designation': 'ENC-' + str(elt.reference),
                    'designation': 'ENCAISSEMENT',
                    'libele_op': ' ',
                    'create_date': elt.date.strftime('%d-%m-%Y'),
                })
                tbl.append(elt.reference)
                print('TBL ENCAISSEMENT', tbl)
                all_data.append(all_vals)
                print()
                print('All Data #5', all_data)
                print()
                amount += elt.amount_currency
                all_vals = {}

        return {
            # 'docs': {},
            'all_data': all_data,
            'amount': amount,
            'start_date': start_date,
            'end_date': end_date,
            'total_final': past_amount_currency + total_amount_currency,
            'total_ant': past_amount_currency,
            'name': name,
            'street': street,
            'date': Date,
        }
