import java.util.Map;

public final class ReserveOperation extends AbstractOperation {
    public ReserveOperation(Warehouse warehouse) {
        super(warehouse);
    }

    @Override
    protected Map<String, Object> execute() {
        return warehouse().reserveAll();
    }
}
