# -*- coding: utf-8 -*-
{
    'name': "Tableau de bord customisé",

    'summary': """Module présentant le tableau de bord des modules ventes, achats, ...""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Amara",
    'website': "https://www.progistack.com",
    'company': 'Progistack',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Tableau de bord',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base',
                'web', 
                'web_dashboard', 
                'board', 
                
                'sale_enterprise', 
                
                'purchase_enterprise', 
                
                'pos_dashboard'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',

        'views/board_views.xml',
        'views/sale_dashboard.xml',
        'views/purchase_dashboard.xml',
        'views/menu.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'dashboard/static/src/js/pivot_model.js',
            # 'dashboard/static/src/js/bundle/**/*.js',
            # 'dashboard/static/src/js/assets/graph/graph_view.js',
        ],
        'web.assets_frontend': [

        ],
        'web.assets_qweb': [
            # 'dashboard/views/graph_view.xml',
            # 'dashboard/static/src/js/bundle/**/*.xml',
            'dashboard/static/src/xml/views_squeleton.xml',

        ]
    },
}
