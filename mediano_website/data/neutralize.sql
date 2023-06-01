-- disable delivery carriers
UPDATE product_product
   SET prod_environment = false,
       active = false;

-- disable delivery carriers
UPDATE delivery_carrier
   SET prod_environment = false,
       active = false;