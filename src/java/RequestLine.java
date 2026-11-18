import java.math.BigDecimal;
public final class RequestLine {
    private final String productId;
    private final BigDecimal quantity;
    public RequestLine(String productId, BigDecimal quantity) {
        this.productId = productId; this.quantity = quantity;
    }
    public String productId() { return productId; }
    public BigDecimal quantity() { return quantity; }
}
