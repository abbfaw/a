# -*- coding: utf-8 -*-
{
    'name': "matarshop_pos",

    'summary': """
        custom pos module for matarshop""",

    'description': """
        custom pos module for matarshop
    """,

    'author': "progistack",
    'website': "https://www.progistack.com",
    'category': 'Sales/Point of Sale',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['point_of_sale', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/cash_in_out.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'matarshop_pos/static/js/InheritCashMovePopup.js',
            'matarshop_pos/static/js/ClosePosPopup.js',
            'matarshop_pos/static/js/CashMoveButton.js',
            'matarshop_pos/static/xml/InheritCashMovePopup.xml',
            'matarshop_pos/static/xml/ClosePosPopup.xml',
        ]

    }
}
