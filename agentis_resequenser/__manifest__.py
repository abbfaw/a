# -*- coding: utf-8 -*-
{
    'name': "agentis_resequenser",

    'summary': """
        mettre a jour la sequence""",

    'description': """
        mettre a jour la sequence
    """,

    'author': "progistack",
    'website': "http://www.progistack.com",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move_views.xml',
    ],

}
