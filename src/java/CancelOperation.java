package ru.mirea.furniture;

public final class CancelOperation extends AbstractOperation {
    private final String requestId;
    private final String reason;

    public CancelOperation(Warehouse warehouse, String requestId, String reason) {
        super(warehouse);
        this.requestId = requestId;
        this.reason = reason;
    }

    @Override
    protected OperationResult execute() {
        return warehouse().cancel(requestId, reason);
    }
}
