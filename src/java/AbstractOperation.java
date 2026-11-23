package ru.mirea.furniture;

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
    public final OperationResult apply() {
        try {
            return execute();
        } catch (IllegalArgumentException error) {
            return new OperationResult.Rejected(error.getMessage());
        }
    }

    protected abstract OperationResult execute();
}
