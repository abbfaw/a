odoo.define('pos_delete_orderline.chrome', function (require) {
    "use strict";
    const Chrome = require('point_of_sale.Chrome');
    const Registries = require('point_of_sale.Registries');

    const PosEmployee = (Chrome) => class extends Chrome {
            get headerButtonIsShown(){
                console.log('===========headerButtonIsShown called=============');
                if (this.env.pos.get_cashier().role == 'manager'){
                    return true;
                }
                else if(this.env.pos.get_cashier().role == 'cashier'){
                    return true;
                }
                return false;
            }
            showCashMoveButton() {
                if (this.env.pos.get_cashier().role == 'manager'){
                    return super.showCashMoveButton() && (this.env.pos.get_cashier().role == 'manager')
                }
                else if(this.env.pos.get_cashier().role == 'cashier'){
                    return super.showCashMoveButton() && (this.env.pos.get_cashier().role == 'cashier');
                }
            }
        };
    Registries.Component.extend(Chrome, PosEmployee);

    return Chrome;
});