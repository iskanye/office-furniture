import java.math.BigDecimal;

public final class Stock {
    private final String productId;
    private final BigDecimal quantity;

    public Stock(String productId, BigDecimal quantity) {
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
