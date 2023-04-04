# -*- coding: utf-8 -*
{
    'name': "POS Load Offline",
    'version': '0.2',
    'category': 'Point of Sale',
    'author': 'Dev Happy',
    "summary":
        """
        If you close the Point of Sale screen when the internet is lost, you can completely reload the point of sale screen without internet
        """,
    "description":
        """
        If you close the Point of Sale screen when the internet is lost, you can completely reload the point of sale screen without internet
        """,
    'depends': ['pos_hr', 'pos_restaurant'],
    'data': [
        'data/import_libraries.xml'
    ],
    'qweb': [
        'static/src/xml/*.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            '/pos_load_offline/static/src/js/lib/idb-keyval.js',
            '/pos_load_offline/static/src/js/lib/IndexedDB.js',
            '/pos_load_offline/static/src/js/Models.js',
            '/pos_load_offline/static/src/js/PosWebClient.js',
        ],
        'web.assets_qweb': [
            '/pos_load_offline/static/src/js/assets_backend.js',
            '/pos_load_offline/static/src/js/lib/idb-keyval.js',
            '/pos_load_offline/static/src/js/lib/IndexedDB.js',
            '/pos_load_offline/static/src/js/PosWebClient.js',

        ],

    },
    "live_test_url": 'https://youtu.be/TlAyIiF3eUo',
    "website": 'http://dev-happy.com',
    'price': '99.99',
    'sequence': 0,
    "currency": 'EUR',
    'images': ['static/description/banner.gif'],
    'support': 'dev.odoo.vn@gmail.com',
    'license': 'OPL-1',
}
