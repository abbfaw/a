# -*- coding: utf-8 -*-
{
    'name': "stock report",
    'sequence': -10,

    'description': """
        report stock
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'reports/barcode_print.xml',
        'reports/reportformat.xml',
    ],
    # only loaded in demonstration mode
    'demo': [],
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
