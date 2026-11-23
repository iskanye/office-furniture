public final class ReserveOperation extends AbstractOperation {
    public ReserveOperation(Warehouse warehouse) {
        super(warehouse);
    }

    @Override
    protected OperationResult execute() {
        return warehouse().reserveAll();
    }
}
