-- V1__create_inventory_schema.sql
-- Initial inventory schema for DreamDemo

-- Inventory Items - tracks current stock levels per product
CREATE TABLE inventory_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id BIGINT NOT NULL UNIQUE,
    quantity_available INT NOT NULL DEFAULT 0,
    quantity_reserved INT NOT NULL DEFAULT 0,
    quantity_damaged INT NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_inventory_items_product_id ON inventory_items(product_id);

-- Inventory Batches - tracks individual batches with expiration dates
-- This allows us to implement spoilage logic and FIFO stock management
CREATE TABLE inventory_batch (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id BIGINT NOT NULL,
    batch_number VARCHAR(255) NOT NULL,
    quantity_received INT NOT NULL,
    date_received TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expiration_date DATE NOT NULL,
    quantity_available INT NOT NULL,
    quantity_damaged INT NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, batch_number)
);

CREATE INDEX idx_inventory_batch_product_id ON inventory_batch(product_id);
CREATE INDEX idx_inventory_batch_status ON inventory_batch(status);
CREATE INDEX idx_inventory_batch_expiration ON inventory_batch(expiration_date);

-- Inventory Reservations - tracks reservations for orders
-- Links to orders in the backend system by order_id
CREATE TABLE inventory_reservation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id VARCHAR(255) NOT NULL UNIQUE,
    product_id BIGINT NOT NULL,
    batch_id UUID NOT NULL,
    quantity_reserved INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    committed_at TIMESTAMP WITH TIME ZONE,
    rolled_back_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (batch_id) REFERENCES inventory_batch(id) ON DELETE RESTRICT
);

CREATE INDEX idx_inventory_reservation_order_id ON inventory_reservation(order_id);
CREATE INDEX idx_inventory_reservation_product_id ON inventory_reservation(product_id);
CREATE INDEX idx_inventory_reservation_batch_id ON inventory_reservation(batch_id);
CREATE INDEX idx_inventory_reservation_status ON inventory_reservation(status);
CREATE INDEX idx_inventory_reservation_expires_at ON inventory_reservation(expires_at);

-- Inventory Transactions - audit log of all inventory movements
-- Provides full traceability of what happened and why
CREATE TABLE inventory_transaction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id BIGINT NOT NULL,
    batch_id UUID,
    transaction_type VARCHAR(50) NOT NULL,
    quantity_change INT NOT NULL,
    reason TEXT,
    order_id VARCHAR(255),
    reservation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    FOREIGN KEY (batch_id) REFERENCES inventory_batch(id) ON DELETE SET NULL,
    FOREIGN KEY (reservation_id) REFERENCES inventory_reservation(id) ON DELETE SET NULL
);

CREATE INDEX idx_inventory_transaction_product_id ON inventory_transaction(product_id);
CREATE INDEX idx_inventory_transaction_batch_id ON inventory_transaction(batch_id);
CREATE INDEX idx_inventory_transaction_order_id ON inventory_transaction(order_id);
CREATE INDEX idx_inventory_transaction_type ON inventory_transaction(transaction_type);
CREATE INDEX idx_inventory_transaction_created_at ON inventory_transaction(created_at);

-- View for quick availability checks
CREATE VIEW product_availability AS
SELECT
    ii.product_id,
    ii.quantity_available,
    ii.quantity_reserved,
    ii.quantity_damaged,
    (ii.quantity_available - ii.quantity_reserved) as quantity_free,
    CASE
        WHEN (ii.quantity_available - ii.quantity_reserved) > 10 THEN 'IN_STOCK'
        WHEN (ii.quantity_available - ii.quantity_reserved) > 0 THEN 'LOW_STOCK'
        ELSE 'OUT_OF_STOCK'
    END as status,
    ii.last_updated as as_of
FROM inventory_items ii;
