# -*- coding: utf-8 -*-
{
    'name' : 'Transfer',
    'version' : '1.0',
    'summary': 'Money transfer and tracking',
    'author' : 'Progistack',
    'sequence': 13,
    'description': """
    Dev by Progistack
    """,
    'category': 'Money transfer',
    'website': 'https://www.progistack.com',
    'depends': ['contacts', 'mail', 'base'],
    'data': [
        'data/transfer_reference.xml',
        'security/ir.model.access.csv',
        'views/balance_view.xml',
        'views/vendor_balance_view.xml',
        'views/transfer_view.xml',
        'views/vendor_view.xml',
        'views/cashflow_view.xml',
        'views/gainflow_view.xml',
        'views/vendor_payment_view.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'application': True,
    'assets': {},
    'license': 'LGPL-3',
}
