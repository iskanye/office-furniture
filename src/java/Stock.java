package ru.mirea.furniture;

import java.math.BigDecimal;

public final class Stock {
    private final String productId;
    private final BigDecimal quantity;

    public Stock(String productId, BigDecimal quantity) {
        if (quantity == null || quantity.scale() > 0 || quantity.signum() < 0) {
            throw new IllegalArgumentException("quantity: ожидается неотрицательное целое число");
        }
        this.productId = productId;
        this.quantity = quantity;
    }

    public String productId() {
        return productId;
    }

    public BigDecimal quantity() {
        return quantity;
    }
}
