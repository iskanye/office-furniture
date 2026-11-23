import java.util.Map;
import java.util.Objects;

public abstract class AbstractOperation implements Operation {
    private final Warehouse warehouse;

    protected AbstractOperation(Warehouse warehouse) {
        this.warehouse = Objects.requireNonNull(warehouse);
    }

    protected final Warehouse warehouse() {
        return warehouse;
    }

    @Override
    public final Map<String, Object> apply() {
        try {
            return execute();
        } catch (IllegalArgumentException error) {
            return Operation.rejected(error.getMessage());
        }
    }

    protected abstract Map<String, Object> execute();
}
