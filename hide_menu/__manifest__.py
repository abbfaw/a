# -*- coding: utf-8 -*-
{
    'name': "Masquer menus et/ou sous-menus",

    'summary': """Masque les menus et/ou sous-menus des utilisateur""",

    'description': """
        Masque les menus et/ou sous-menus des utilisateur   
    """,

    'author': "Progistack",
    'maintainer': 'Tano Martin',
    'website': "https://www.progistack.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'management user',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'views/res_users.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
