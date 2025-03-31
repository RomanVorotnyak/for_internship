CREATE TABLE Employee (
    employee_id    SERIAL        PRIMARY KEY,
    last_name      VARCHAR(100)  NOT NULL,
    first_name     VARCHAR(100)  NOT NULL,
    middle_name    VARCHAR(100),
    cur_position   VARCHAR(100)  NOT NULL,
    prev_position  VARCHAR(100),
    current_salary NUMERIC(12,2) NOT NULL,
    hire_date      DATE          NOT NULL
);


CREATE TABLE Customer (
    customer_id      SERIAL        PRIMARY KEY,
    last_name        VARCHAR(100)  NOT NULL,
    first_name       VARCHAR(100)  NOT NULL,
    middle_name      VARCHAR(100),
    phone_number     VARCHAR(20),
    email            VARCHAR(100)
);


CREATE TABLE Engine (
    engine_id        SERIAL        PRIMARY KEY,
    brand            VARCHAR(100)  NOT NULL,
    model            VARCHAR(100)  NOT NULL,
    supported_car    VARCHAR(200)  NOT NULL,
    price            NUMERIC(12,2) NOT NULL,
    stock_quantity   INT           NOT NULL DEFAULT 0
);


CREATE TABLE Transmission (
    transmission_id  SERIAL        PRIMARY KEY,
    brand            VARCHAR(100)  NOT NULL,
    model            VARCHAR(100)  NOT NULL,
    supported_car    VARCHAR(200)  NOT NULL,
    price            NUMERIC(12,2) NOT NULL,
    stock_quantity   INT           NOT NULL DEFAULT 0
);


CREATE TABLE Consumable (
    consumable_id    SERIAL        PRIMARY KEY,
    name             VARCHAR(200)  NOT NULL,
    brand            VARCHAR(100)  NOT NULL,
    supported_car    VARCHAR(200),
    price            NUMERIC(12,2) NOT NULL,
    stock_quantity   INT           NOT NULL DEFAULT 0
);


CREATE TABLE "Order" (
    order_id         SERIAL        PRIMARY KEY,
    order_date       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    employee_id      INT           NOT NULL,
    customer_id      INT           NOT NULL,
    total_amount     NUMERIC(12,2) NOT NULL DEFAULT 0,
    CONSTRAINT fk_order_employee
        FOREIGN KEY (employee_id)
        REFERENCES Employee(employee_id),
    CONSTRAINT fk_order_customer
        FOREIGN KEY (customer_id)
        REFERENCES Customer(customer_id)
);


CREATE TABLE Order_engine (
    order_id         INT           NOT NULL,
    engine_id        INT           NOT NULL,
    quantity         INT           NOT NULL,
    price_at_moment  NUMERIC(12,2) NOT NULL,
    PRIMARY KEY(order_id, engine_id),
    CONSTRAINT fk_oe_order
        FOREIGN KEY (order_id)
        REFERENCES "Order"(order_id),
    CONSTRAINT fk_oe_engine
        FOREIGN KEY (engine_id)
        REFERENCES Engine(engine_id)
);


CREATE TABLE Order_transmission (
    order_id         INT           NOT NULL,
    transmission_id  INT           NOT NULL,
    quantity         INT           NOT NULL,
    price_at_moment  NUMERIC(12,2) NOT NULL,
    PRIMARY KEY(order_id, transmission_id),
    CONSTRAINT fk_ot_order
        FOREIGN KEY (order_id)
        REFERENCES "Order"(order_id),
    CONSTRAINT fk_ot_transmission
        FOREIGN KEY (transmission_id)
        REFERENCES Transmission(transmission_id)
);


CREATE TABLE Order_consumable (
    order_id         INT           NOT NULL,
    consumable_id    INT           NOT NULL,
    quantity         INT           NOT NULL,
    price_at_moment  NUMERIC(12,2) NOT NULL,
    PRIMARY KEY(order_id, consumable_id),
    CONSTRAINT fk_oc_order
        FOREIGN KEY (order_id)
        REFERENCES "Order"(order_id),
    CONSTRAINT fk_oc_consumable
        FOREIGN KEY (consumable_id)
        REFERENCES Consumable(consumable_id)
);

