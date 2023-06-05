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
                const values = [{'name': ' ', 'value': 1},{'name': 'مساعدة', 'value': 2},
                 {'name': 'قهوة وماء', 'value': 3},{'name': 'مياه الشركة', 'value': 4},
                 {'name': 'إشتراك مولد', 'value': 5},{'name': 'كهرباء الدولة ', 'value': 6},
                 {'name': 'نقل البضاعة', 'value': 7},{'name': 'الواجهة', 'value': 8},
                 {'name': 'السنتر', 'value': 9},{'name': 'انترنت ', 'value': 10},
                 {'name': 'صيانة ', 'value': 11},{'name': 'مصاريف السفر', 'value': 12},
                 {'name': 'الشحن', 'value': 13},{'name': 'ابو جاد', 'value': 14},
                 {'name': 'حسان', 'value': 15},{'name': 'ميساء', 'value': 16},
                 {'name': 'آية', 'value': 17},{'name': 'Popy ', 'value': 18},{'name': 'Top boy ', 'value': 19},
                 {'name': 'Tatoo', 'value': 20},{'name': 'Baby kid ', 'value': 21},{'name': 'Sokkar', 'value': 22},
                 {'name': 'New boy', 'value': 23},{'name': 'Daaboul ', 'value': 24},{'name': 'Kidea  ', 'value': 25},
                 {'name': 'Turque', 'value': 26}]
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