odoo.define('point_of_sale.NumberBuffer', function(require) {
    'use strict';

    const { useListener } = require("@web/core/utils/hooks");
    const { parse } = require('web.field_utils');
    const { barcodeService } = require('@barcodes/barcode_service');
    const { _t } = require('web.core');
    const { Gui } = require('point_of_sale.Gui');
    const session = require('web.session');

    const { EventBus, onMounted, onWillUnmount, useComponent, useExternalListener } = owl;
    const INPUT_KEYS = new Set(
        ['Delete', 'Backspace', '+1', '+2', '+5', '+10', '+20', '+50'].concat('0123456789+-.,'.split(''))
    );
    const CONTROL_KEYS = new Set(['Enter', 'Esc']);
    const ALLOWED_KEYS = new Set([...INPUT_KEYS, ...CONTROL_KEYS]);
    const getDefaultConfig = () => ({
        decimalPoint: false,
        triggerAtEnter: false,
        triggerAtEsc: false,
        triggerAtInput: false,
        nonKeyboardInputEvent: false,
        useWithBarcode: false,
    });

    /**
     * This is a singleton.
     *
     * Only one component can `use` the buffer at a time.
     * This is done by keeping track of each component (and its
     * corresponding state and config) using a stack (bufferHolderStack).
     * The component on top of the stack is the one that currently
     * `holds` the buffer.
     *
     * When the current component is unmounted, the top of the stack
     * is popped and NumberBuffer is set up again for the new component
     * on top of the stack.
     *
     * Usage
     * =====
     * - Activate in the construction of root component. `NumberBuffer.activate()`
     * - Use the buffer in a child component by calling `NumberBuffer.use(<config>)`
     *   in the constructor of the child component.
     * - The component that `uses` the buffer has access to the following instance
     *   methods of the NumberBuffer:
     *   - get()
     *   - set(val)
     *   - reset()
     *   - getFloat()
     *   - capture()
     *
     * Note
     * ====
     * - No need to instantiate as it is a singleton created before exporting in this module.
     *
     * Possible Improvements
     * =====================
     * - Relieve the buffer from responsibility of handling `Enter` and other control keys.
     * - Make the constants (ALLOWED_KEYS, etc.) more configurable.
     * - Write more integration tests. NumberPopup can be used as test component.
     */
    class NumberBuffer extends EventBus {
        constructor() {
            super();
            this.isReset = false;
            this.bufferHolderStack = [];
        }
        /**
         * @returns {String} value of the buffer, e.g. '-95.79'
         */
        get() {
            return this.state ? this.state.buffer : null;
        }
        /**
         * Takes a string that is convertible to float, and set it as
         * value of the buffer. e.g. val = '2.99';
         *
         * @param {String} val
         */
        set(val) {
            this.state.buffer = !isNaN(parseFloat(val)) ? val : '';
            this.trigger('buffer-update', this.state.buffer);
        }
        /**
         * Resets the buffer to empty string.
         */
        reset() {
            this.isReset = true;
            this.state.buffer = '';
            this.trigger('buffer-update', this.state.buffer);
        }
        /**
         * Calling this function, we immediately invoke the `handler` method
         * that handles the contents of the input events buffer (`eventsBuffer`).
         * This is helpful when we don't want to wait for the timeout that
         * is supposed to invoke the handler.
         */
        capture() {
            if (this.handler) {
                clearTimeout(this._timeout);
                this.handler();
                delete this.handler;
            }
        }
        /**
         * @returns {number} float equivalent of the value of buffer
         */
        getFloat() {
            return parse.float(this.get());
        }
        /**
         * Add keyup listener to window via the useExternalListener hook.
         * When the component calling this is unmounted, the listener is also
         * removed from window.
         */
        activate() {
            this.defaultDecimalPoint = _t.database.parameters.decimal_point;
            useExternalListener(window, 'keyup', this._onKeyboardInput.bind(this));
        }
        /**
         * @param {Object} config Use to setup the buffer
         * @param {String|null} config.decimalPoint The decimal character.
         * @param {String|null} config.triggerAtEnter Event triggered when 'Enter' key is pressed.
         * @param {String|null} config.triggerAtEsc Event triggered when 'Esc' key is pressed.
         * @param {String|null} config.triggerAtInput Event triggered for every accepted input.
         * @param {String|null} config.nonKeyboardInputEvent Also listen to a non-keyboard input event
         *      that carries a payload of { key }. The key is checked if it is a valid input. If valid,
         *      the number buffer is modified just as it is modified when a keyboard key is pressed.
         * @param {Boolean} config.useWithBarcode Whether this buffer is used with barcode.
         * @emits config.triggerAtEnter when 'Enter' key is pressed.
         * @emits config.triggerAtEsc when 'Esc' key is pressed.
         * @emits config.triggerAtInput when an input is accepted.
         */
        use(config) {
            this.eventsBuffer = [];
            const currentComponent = useComponent();
            config = Object.assign(getDefaultConfig(), config);
            onMounted(() => {
                this.bufferHolderStack.push({
                    component: currentComponent,
                    state: config.state ? config.state : { buffer: '', toStartOver: false },
                    config,
                });
                this._setUp();
            });
            onWillUnmount(() => {
                this.bufferHolderStack.pop();
                this._setUp();
            });
            // Add listener that accepts non keyboard inputs
            if (typeof config.nonKeyboardInputEvent === 'string') {
                useListener(config.nonKeyboardInputEvent, this._onNonKeyboardInput.bind(this));
            }
        }
        get _currentBufferHolder() {
            return this.bufferHolderStack[this.bufferHolderStack.length - 1];
        }
        _setUp() {
            if (!this._currentBufferHolder) return;
            const { component, state, config } = this._currentBufferHolder;
            this.component = component;
            this.state = state;
            this.config = config;
            this.decimalPoint = config.decimalPoint || this.defaultDecimalPoint;
            this.maxTimeBetweenKeys = this.config.useWithBarcode
                ? barcodeService.maxTimeBetweenKeysInMs
                : 0;
        }
        _onKeyboardInput(event) {
            return this._bufferEvents(this._onInput(event => event.key))(event);
        }
        _onNonKeyboardInput(event) {
            return this._bufferEvents(this._onInput(event => event.detail.key))(event);
        }
        _bufferEvents(handler) {
            return event => {
                if (['INPUT', 'TEXTAREA'].includes(event.target.tagName) || !this.eventsBuffer) return;
                clearTimeout(this._timeout);
                this.eventsBuffer.push(event);
                this._timeout = setTimeout(handler, this.maxTimeBetweenKeys);
                this.handler = handler
            };
        }
        _onInput(keyAccessor) {
            return () => {
                if (this.eventsBuffer.length <= 2) {
                    // Check first the buffer if its contents are all valid
                    // number input.
                    for (let event of this.eventsBuffer) {
                        if (!ALLOWED_KEYS.has(keyAccessor(event))) {
                            this.eventsBuffer = [];
                            return;
                        }
                    }
                    // At this point, all the events in buffer
                    // contains number input. It's now okay to handle
                    // each input.
                    for (let event of this.eventsBuffer) {
                        this._handleInput(keyAccessor(event));
                        event.preventDefault();
                        event.stopPropagation();
                    }
                }
                this.eventsBuffer = [];
            };
        }
       // la methode a été completement revue de v15 à v16 
        // la methode est faite pour voir ce qui est saisie au clavier et en fonction exceter des actions 
        _handleInput(key) {
            console.log('===========hasManuelDiscount called=============');
          
            const managerPromise = session.user_has_group('point_of_sale.group_pos_manager');
            const responsablePromise = session.user_has_group('pos_delete_orderline.group_pos_reponsable_user');
            const utilisateurPromise = session.user_has_group('point_of_sale.group_pos_user');
          
            Promise.all([managerPromise, responsablePromise, utilisateurPromise])
              .then(([manager, responsable, utilisateur]) => {
                console.log('=====manager======', manager, '=================');
                console.log('======repos=====', responsable, '=================');
                console.log('======uti=====', utilisateur, '=================');

                if (key === 'Enter' && this.config.triggerAtEnter) {
                    this.component.trigger(this.config.triggerAtEnter, this.state);
                } else if (key === 'Esc' && this.config.triggerAtEsc) {
                    this.component.trigger(this.config.triggerAtEsc, this.state);
                } else if (key === 'Backspace' || key === 'Delete'){
                // lorsque l'utilisateur click sur la touche Backspace ou Delete on verifie dans cashier le statut(manager ou utilisateur) de l'utilisateur connnecté
                    const cashier = this.component.env.pos.get_cashier()
                    if (manager) {
                        // si l'utilisateur est manager nous pouvons supprimer une ligne
                        this._updateBuffer(key);
                        if (this.config.triggerAtInput)
                            this.component.trigger(this.config.triggerAtInput, { buffer: this.state.buffer, key });
                    }else if (responsable && !manager) {
                        // si l'utilisateur est manager nous pouvons supprimer une ligne
                        this._updateBuffer(key);
                        if (this.config.triggerAtInput)
                            this.component.trigger(this.config.triggerAtInput, { buffer: this.state.buffer, key });
                    }else if(utilisateur && !responsable && !manager){
                        // sinon un le message d'eurreur si dessous apparait
                        const { confirmed, payload } = Gui.showPopup('ErrorPopup', {
                            title: _t('Autorisation'),
                            body: _t("Vous ne pouvez pas supprimer un article dans le panier, attribuer une quantité négative ou le mettre à 0, veuillez contacter votre Responsable."),
                        })
                    }
                    }else if (INPUT_KEYS.has(key)) {
                        this._updateBuffer(key);
                        if (this.config.triggerAtInput)
                            this.component.trigger(this.config.triggerAtInput, { buffer: this.state.buffer, key });
                    }
                })
                    .catch((error) => {
                        console.error(error);
                        // Gérer les erreurs potentielles ici
                      });
                    // Le reste de votre code...
                }
        /**
         * Updates the current buffer state using the given input.
         * @param {String} input valid input
         */
        _updateBuffer(input) {
            const isEmpty = val => {
                return val === '' || val === null;
            };
            if (input === undefined || input === null) return;
            let isFirstInput = isEmpty(this.state.buffer);
            if (input === ',' || input === '.') {
                if (this.state.toStartOver) {
                    this.state.buffer = '';
                }
                if (isFirstInput) {
                    this.state.buffer = '0' + this.decimalPoint;
                } else if (!this.state.buffer.length || this.state.buffer === '-') {
                    this.state.buffer += '0' + this.decimalPoint;
                } else if (this.state.buffer.indexOf(this.decimalPoint) < 0) {
                    this.state.buffer = this.state.buffer + this.decimalPoint;
                }
            } else if (input === 'Delete') {
                if (this.isReset) {
                    this.state.buffer = '';
                    this.isReset = false;
                    return;
                }
                this.state.buffer = isEmpty(this.state.buffer) ? null : '';
            } else if (input === 'Backspace') {
                if (this.isReset) {
                    this.state.buffer = '';
                    this.isReset = false;
                    return;
                }
                if (this.state.toStartOver) {
                    this.state.buffer = '';
                }
                const buffer = this.state.buffer;
                if (isEmpty(buffer)) {
                    this.state.buffer = null;
                } else {
                    const nCharToRemove = buffer[buffer.length - 1] === this.decimalPoint ? 2 : 1;
                    this.state.buffer = buffer.substring(0, buffer.length - nCharToRemove);
                }
            } else if (input === '+') {
                if (this.state.buffer[0] === '-') {
                    this.state.buffer = this.state.buffer.substring(1, this.state.buffer.length);
                }
            } else if (input === '-') {
                if (isFirstInput) {
                    this.state.buffer = '-0';
                } else if (this.state.buffer[0] === '-') {
                    this.state.buffer = this.state.buffer.substring(1, this.state.buffer.length);
                } else {
                    this.state.buffer = '-' + this.state.buffer;
                }
            } else if (input[0] === '+' && !isNaN(parseFloat(input))) {
                // when input is like '+10', '+50', etc
                const inputValue = parse.float(input.slice(1));
                const currentBufferValue = this.state.buffer ? parse.float(this.state.buffer) : 0;
                this.state.buffer = this.component.env.pos.formatFixed(
                    inputValue + currentBufferValue
                );
            } else if (!isNaN(parseInt(input, 10))) {
                if (this.state.toStartOver) {  // when we want to erase the current buffer for a new value
                    this.state.buffer = '';
                }
                if (isFirstInput) {
                    this.state.buffer = '' + input;
                } else if (this.state.buffer.length > 12) {
                    Gui.playSound('bell');
                } else {
                    this.state.buffer += input;
                }
            }
            if (this.state.buffer === '-') {
                this.state.buffer = '';
            }
            // once an input is accepted and updated the buffer,
            // the buffer should not be in reset state anymore.
            this.isReset = false;
            // it should not be in a start the buffer over state anymore.
            this.state.toStartOver = false;

            if (this.config.maxValue && this.state.buffer > this.config.maxValue) {
                this.state.buffer = this.config.maxValue.toString();
                this.config.maxValueReached();
            }

            this.trigger('buffer-update', this.state.buffer);
        }
    }

    return new NumberBuffer();
});
