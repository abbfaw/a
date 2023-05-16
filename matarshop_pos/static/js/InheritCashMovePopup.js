odoo.define('matarshop_pos.InheritCashMovePopup', function (require) {
    'use strict';

    const CashMovePopup = require('point_of_sale.CashMovePopup');
    const Registries = require('point_of_sale.Registries');
    const { useRef, useState, setState } = owl;

    const InheritCashMovePopup = (CashMovePopup) =>
        class extends CashMovePopup {
            setup() {
                super.setup();
                this.state = useState({
                inputComment: '',
                inputType: '', // '' | 'in' | 'out'
                inputAmount: '',
                inputReason: '',
                inputHasError: false,
                });
            }
            reasonValues(){
                const values = [{'name': ' ', 'value': 1},{'name': 'Avance sur salaire', 'value': 2},
                 {'name': 'Taxi', 'value': 3},{'name': 'Salaire', 'value': 4},
                 {'name': 'CIE', 'value': 5},{'name': 'SODECI', 'value': 6},
                 {'name': 'Matériels de nettoyage', 'value': 7},{'name': 'Matériels caisse', 'value': 8},{'name': 'Autres', 'value': 9}]
                return values
        }
        confirm() {
            if ((this.state.inputComment.trim() == '') && (this.state.inputReason.trim() == 'Autres')){
                this.state.inputHasError = true;
                this.errorMessage = this.env._t('Veuillez mettre une description svp !');
                return;
            }
            return super.confirm();
        }

        getPayload() {
            let data = super.getPayload()
            data.comment = this.state.inputComment.trim();
            console.log('data ....in data .', data);
            return data ;
        }
    };
    Registries.Component.extend(CashMovePopup, InheritCashMovePopup);

    return InheritCashMovePopup;
});