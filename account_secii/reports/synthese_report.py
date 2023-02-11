from odoo import models, api, fields
from datetime import datetime
import pytz
import pprint


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
        print('tu es mt 07571.........10861', data)
        partner_id = data.get('partner')
        start_date = datetime.strptime(data.get('start_date'), '%d-%m-%Y')
        end_date = datetime.strptime(data.get('end_date'), '%d-%m-%Y')
        scrap = self.env['res.partner'].sudo().search([('id', '=', partner_id)])
        name = scrap.name
        street = scrap.street
        Date = datetime.now().strftime('%Y-%m-%d')
        tracking = self.env['tracking.partner'].sudo()
        sale_order = self.env['sale.order'].sudo()
        purchase_order = self.env['purchase.order'].sudo()
        account_move = self.env['account.move'].sudo()
        account_payment = self.env['account.payment'].sudo()
        secii_encaissement = self.env['secii.encaissement'].sudo()
        # retour = self.env['purchase.order'].sudo()
        print('partner_id', partner_id)

        """ Recherche des IDS de tous les modules """
        find_account_move_id = account_move.search(
            [('partner_id', '=', partner_id), ('create_date', '>=', start_date), ('create_date', '<=', end_date),
             ('state', '=', 'posted'), ('move_type', 'in', ('out_invoice', 'out_refund'))])
        print('FActure', find_account_move_id)

        find_account_payment_id = account_payment.search(
            [('partner_id', '=', partner_id), ('create_date', '>=', start_date), ('create_date', '<=', end_date),
             ('state', '=', 'posted'), ('partner_type', '=', 'customer')])

        find_sale_order_id = sale_order.search(
            [('partner_id', '=', partner_id), ('create_date', '>=', start_date), ('create_date', '<=', end_date),
             ('is_prive', '=', True), ('state', '=', 'sale')])

        find_purchase_order_id = purchase_order.search(
            [('partner_id', '=', partner_id), ('create_date', '>=', start_date), ('create_date', '<=', end_date),
             ('state', '=', 'purchase'), ('is_prive', '=', True), ('retour', '=', True), ])

        find_secii_encaissement_id = secii_encaissement.search(
            [('partenaire', '=', partner_id), ('create_date', '>=', start_date), ('create_date', '<=', end_date),
             ('instance', '=', True), ('status', '=', 'paye')])

        """concaténation de toutes les Dates"""
        all_date = find_sale_order_id.mapped('date_effective') + find_purchase_order_id.mapped(
            'create_date') + find_account_move_id.mapped('create_date') + find_account_payment_id.mapped(
            'create_date') + find_secii_encaissement_id.mapped('create_date')
        tri_date = sorted(all_date)
        print('ALL DATE', tri_date)

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
        for date in tri_date:
            """Ventes +"""
            for so in find_sale_order_id:
                tracking_orders = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('purchase_ref', '=', str(so.id) + 'VEN')])
                print('Tracking ------ Orders ..', tracking_orders)
                if tracking_orders:
                    if tracking_orders.purchase_ref not in tbl:
                        all_vals.update({
                            'name': tracking_orders.reference,
                            'partner_id': tracking_orders.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_orders.amount_currency,
                            'debit': tracking_orders.amount_currency,
                            'credit': 0,
                            'libele': ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_orders.amount_currency,
                            # 'designation': 'BL-' + str(tracking_orders.reference),
                            'designation': 'VENTE',
                            'libele_op': tracking_orders.libele_op or ' ',
                            'create_date': tracking_orders.date.strftime('%d-%m-%Y'),
                        })
                        tbl.append(tracking_orders.purchase_ref)
                        all_data.append(all_vals)
                        print()
                        print('All Data #1', all_data)
                        print()
                        amount += tracking_orders.amount_currency
                        all_vals = {}

            """Achats +"""
            for po in find_purchase_order_id:
                tracking_purchases = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('purchase_ref', '=', str(po.id) + 'ACH')])
                print('Tracking ------ Purchases ..', tracking_purchases)
                if tracking_purchases:
                    if tracking_purchases.purchase_ref not in tbl:
                        all_vals.update({
                            'name': tracking_purchases.reference,
                            'partner_id': tracking_purchases.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_purchases.amount_currency,
                            'debit': 0,
                            'credit': tracking_purchases.amount_currency,
                            'libele': tracking_purchases.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_purchases.amount_currency,
                            # 'designation': 'BL-' + str(tracking_purchases.reference),
                            'designation': "RETOUR D'ACHAT",
                            'libele_op': ' ',
                            'create_date': tracking_purchases.date.strftime('%d-%m-%Y'),
                        })
                        tbl.append(tracking_purchases.purchase_ref)
                        all_data.append(all_vals)
                        print()
                        print('All Data #2', all_data)
                        print()
                        amount += tracking_purchases.amount_currency
                        all_vals = {}

            """Factures +"""
            for am in find_account_move_id:
                tracking_factures = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('move_id', '=', am.id),
                     ('partner_type', '=', 'customer')])
                print('Tracking ------ Factures ..', tracking_factures)
                if tracking_factures:
                    if tracking_factures.reference not in tbl:
                        all_vals.update({
                            'name': tracking_factures.reference,
                            'partner_id': tracking_factures.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_factures.amount_currency,
                            'debit': tracking_factures.amount_currency,
                            'credit': 0,
                            'libele': tracking_factures.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_factures.amount_currency,
                            # 'designation': str(tracking_factures.reference),
                            'designation': 'FACTURE',
                            'libele_op': ' ',
                            'create_date': tracking_factures.date.strftime('%d-%m-%Y'),
                        })
                        tbl.append(tracking_factures.reference)
                        all_data.append(all_vals)
                        print()
                        print('All Data #3', all_data)
                        print()
                        amount += tracking_factures.amount_currency
                        all_vals = {}

            """Paiements -"""
            for ap in find_account_payment_id:
                tracking_payments = tracking.search(
                    [('partner', '=', partner_id), ('date', '=', date), ('payment_id', '=', ap.id),
                     ('partner_type', '=', 'customer')])
                print('Tracking ------ Payments ..', tracking_payments)
                if tracking_payments:
                    if tracking_payments.reference not in tbl:
                        all_vals.update({
                            'name': tracking_payments.reference,
                            'partner_id': tracking_payments.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_payments.amount_currency,
                            'debit': 0,
                            'credit': tracking_payments.amount_currency,
                            'libele': tracking_payments.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_payments.amount_currency,
                            # 'designation': str(tracking_payments.reference),
                            'designation': 'PAIEMENT',
                            'libele_op': ' ',
                            'create_date': tracking_payments.date.strftime('%d-%m-%Y'),
                        })
                        tbl.append(tracking_payments.reference)
                        print('TBL PAIEMENT', tbl)
                        all_data.append(all_vals)
                        print()
                        print('All Data #4', all_data)
                        print()
                        amount += tracking_payments.amount_currency
                        all_vals = {}

            """Encaissements -"""
            for se in find_secii_encaissement_id:
                print('ENC ## 1', str(se.id) + 'ENC', se.num_seq)
                tracking_encaissements = tracking.search([('partner', '=', partner_id), ('date', '=', date.strftime('%d-%m-%Y')), ('purchase_ref', '=', str(se.id) + 'ENC')])
                print('Tracking ------ Encaissements ..', tracking_encaissements)
                if tracking_encaissements:
                    if tracking_encaissements.reference not in tbl:
                        all_vals.update({
                            'name': tracking_encaissements.reference,
                            'partner_id': tracking_encaissements.partner.name,
                            # 'user_id': tracking_orders.user_id.name,
                            'amount_total': tracking_encaissements.amount_currency,
                            'debit': 0,
                            'credit': tracking_encaissements.amount_currency,
                            'libele': tracking_encaissements.libele_op or ' ',
                            'somme_paye': 0,
                            'solde': amount + tracking_encaissements.amount_currency,
                            # 'designation': 'ENC-' + str(tracking_encaissements.reference),
                            'designation': 'ENCAISSEMENT',
                            'libele_op': ' ',
                            'create_date': tracking_encaissements.date.strftime('%d-%m-%Y'),
                        })
                        tbl.append(tracking_encaissements.reference)
                        print('TBL ENCAISSEMENT', tbl)
                        all_data.append(all_vals)
                        print()
                        print('All Data #5', all_data)
                        print()
                        amount += tracking_encaissements.amount_currency
                        all_vals = {}
            print('AMT', amount)

        print('all_vals =>', all_vals)
        print('Tbl ===>', tbl)
        print('all_data ', all_data)
        tracking_partner = self.env['tracking.partner'].search([('id', '=', data.get('id'))])
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
