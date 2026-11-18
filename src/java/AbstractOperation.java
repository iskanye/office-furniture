import java.util.*;
public abstract class AbstractOperation implements Operation {
    private final Warehouse warehouse;
    protected AbstractOperation(Warehouse warehouse) { this.warehouse = Objects.requireNonNull(warehouse); }
    protected final Warehouse warehouse() { return warehouse; }
    @Override public final Map<String, Object> apply() { return execute(); }
    protected abstract Map<String, Object> execute();
}
