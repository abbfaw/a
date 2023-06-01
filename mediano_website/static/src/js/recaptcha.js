odoo.define('my_module.recaptcha_handler', function (require) {
  "use strict";

  var ajax = require('web.ajax');
  var core = require('web.core');
  var _t = core._t;

  ajax.jsonRpc('/recaptcha/status', 'call', {}).then(function (data) {
    if (data.recaptcha_status) {
      // Récupération de la valeur du champ dans ir.config_parameter
      var show_recaptcha = data.show_recaptcha;

      if (show_recaptcha) {
        // Affichage du recaptcha
      } else {
        // Masquage du recaptcha
      }
    }
  });
});
