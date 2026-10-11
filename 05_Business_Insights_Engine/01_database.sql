DROP TABLE IF EXISTS order_items, invoices, products, customers, raw_retail CASCADE;

CREATE TABLE raw_retail (
    raw_id BIGSERIAL PRIMARY KEY,
    invoice_no TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    invoice_date TIMESTAMP NOT NULL,
    unit_price NUMERIC(14, 4) NOT NULL,
    customer_id BIGINT,
    country TEXT NOT NULL,
    load_status TEXT NOT NULL DEFAULT 'loaded',
    exclusion_reason TEXT
);

CREATE TABLE customers (
    customer_id BIGINT PRIMARY KEY,
    country TEXT NOT NULL
);

CREATE TABLE products (
    stock_code TEXT PRIMARY KEY,
    description TEXT
);

CREATE TABLE invoices (
    invoice_no TEXT PRIMARY KEY,
    customer_id BIGINT REFERENCES customers(customer_id),
    invoice_date TIMESTAMP NOT NULL,
    country TEXT NOT NULL,
    is_cancelled BOOLEAN NOT NULL
);

CREATE TABLE order_items (
    item_id BIGINT PRIMARY KEY REFERENCES raw_retail(raw_id),
    invoice_no TEXT NOT NULL REFERENCES invoices(invoice_no),
    stock_code TEXT NOT NULL REFERENCES products(stock_code),
    quantity INTEGER NOT NULL,
    unit_price NUMERIC(14, 4) NOT NULL
);

CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_customer ON invoices(customer_id);
CREATE INDEX idx_invoices_country ON invoices(country);
CREATE INDEX idx_invoices_cancelled ON invoices(is_cancelled);
CREATE INDEX idx_order_items_invoice ON order_items(invoice_no);
CREATE INDEX idx_order_items_stock ON order_items(stock_code);
