import java.math.BigDecimal;

public final class Reservation {
    private final String id;
    private final String requestId;
    private final String productId;
    private final BigDecimal quantity;
    private boolean active;

    public Reservation(
            String id, String requestId, String productId, BigDecimal quantity, boolean active) {
        this.id = id;
        this.requestId = requestId;
        this.productId = productId;
        this.quantity = quantity;
        this.active = active;
    }

    public String id() {
        return id;
    }

    public String requestId() {
        return requestId;
    }

    public String productId() {
        return productId;
    }

    public BigDecimal quantity() {
        return quantity;
    }

    public boolean active() {
        return active;
    }

    public void release() {
        active = false;
    }
}
