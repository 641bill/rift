import java.util.Arrays;
import java.util.ArrayList;
import jdk.internal.rift.RiftRegion;

public final class RiftHotSpotObjectRegionSmoke {
    private static final int OPEN = 1;
    private static final int USED = 4;
    private static final int HIGH_WATER = 5;
    private static final int CLOSES = 9;
    private static final int RESETS = 10;
    private static final int OBJECT_ALLOCS = 12;
    private static Object escapedStatic;
    private static Object[] escapedArray;
    private static Holder escapedHolder;

    public static void main(String[] args) {
        RiftRegion.registerEligible(PrimitiveRecord.class);
        expectIllegalArgument(() -> RiftRegion.registerEligible(ReferenceRecord.class), "reference field eligibility");
        expectIllegalArgument(() -> RiftRegion.registerEligible(NonFinalRecord.class), "non-final eligibility");

        final long[] handle = new long[1];
        final long[] checksum = new long[1];
        RiftRegion.epoch(4096, () -> {
            handle[0] = RiftRegion.current();
            PrimitiveRecord record = new PrimitiveRecord(7, 11L, 3.5d);
            checksum[0] = record.sum();
            long[] active = RiftRegion.stats(handle[0]);
            check(active[OPEN] == 1, "region is open: " + Arrays.toString(active));
            check(active[USED] > 0, "object allocation used region bytes: " + Arrays.toString(active));
            check(active[OBJECT_ALLOCS] == 1, "object allocation count: " + Arrays.toString(active));
        });

        check(checksum[0] == 21L, "constructor and field stores ran normally");
        long[] closed = RiftRegion.stats(handle[0]);
        check(closed[OPEN] == 0, "region closed: " + Arrays.toString(closed));
        check(closed[USED] == 0, "region reset used bytes: " + Arrays.toString(closed));
        check(closed[HIGH_WATER] > 0, "high water retained: " + Arrays.toString(closed));
        check(closed[CLOSES] == 1, "close count: " + Arrays.toString(closed));
        check(closed[RESETS] == 1, "reset count: " + Arrays.toString(closed));
        check(closed[OBJECT_ALLOCS] == 1, "closed object allocation count: " + Arrays.toString(closed));

        checkUnregisteredFallsBackToHeap();
        checkStaticRetentionRejected();
        checkArrayRetentionRejected();
        checkObjectFieldRetentionRejected();
        checkGenericHeapRetentionRejected();
        checkArrayListRetentionRejected();
        System.out.println("object-enabled-ok");
    }

    private static void checkUnregisteredFallsBackToHeap() {
        final long[] handle = new long[1];
        final long[] checksum = new long[1];
        RiftRegion.epoch(1024, () -> {
            handle[0] = RiftRegion.current();
            UnregisteredRecord record = new UnregisteredRecord(42);
            checksum[0] = record.x;
        });
        long[] closed = RiftRegion.stats(handle[0]);
        check(checksum[0] == 42L, "unregistered heap fallback constructor ran");
        check(closed[OBJECT_ALLOCS] == 0, "unregistered class should not use region object path: " + Arrays.toString(closed));
    }

    private static void checkStaticRetentionRejected() {
        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        try {
            PrimitiveRecord record = new PrimitiveRecord(1, 2L, 3.0d);
            check(RiftRegion.stats(handle)[OBJECT_ALLOCS] == 1, "static test record should allocate in region");
            try {
                escapedStatic = record;
                throw new AssertionError("static heap retention should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
        } finally {
            escapedStatic = null;
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }
    }

    private static void checkArrayRetentionRejected() {
        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        try {
            PrimitiveRecord record = new PrimitiveRecord(2, 3L, 4.0d);
            Object[] holder = new Object[1];
            escapedArray = holder;
            try {
                holder[0] = record;
                throw new AssertionError("array heap retention should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
        } finally {
            if (escapedArray != null) {
                escapedArray[0] = null;
            }
            escapedArray = null;
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }
    }

    private static void checkObjectFieldRetentionRejected() {
        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        try {
            PrimitiveRecord record = new PrimitiveRecord(3, 4L, 5.0d);
            Holder holder = new Holder();
            escapedHolder = holder;
            try {
                holder.value = record;
                throw new AssertionError("object-field heap retention should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
        } finally {
            if (escapedHolder != null) {
                escapedHolder.value = null;
            }
            escapedHolder = null;
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }
    }

    private static void checkGenericHeapRetentionRejected() {
        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        try {
            PrimitiveRecord record = new PrimitiveRecord(4, 5L, 6.0d);
            Object widened = record;
            try {
                new GenericCell<Object>(widened);
                throw new AssertionError("generic heap retention should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
        } finally {
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }
    }

    private static void checkArrayListRetentionRejected() {
        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        try {
            PrimitiveRecord record = new PrimitiveRecord(5, 6L, 7.0d);
            ArrayList<Object> list = new ArrayList<Object>();
            try {
                list.add(record);
                throw new AssertionError("ArrayList heap retention should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
        } finally {
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }
    }

    private static void expectIllegalArgument(Runnable body, String label) {
        try {
            body.run();
            throw new AssertionError(label + " should fail");
        } catch (IllegalArgumentException expected) {
            // expected
        }
    }

    private static void check(boolean condition, String message) {
        if (!condition) {
            throw new AssertionError(message);
        }
    }

    public static final class PrimitiveRecord {
        private int x;
        private long y;
        private double z;

        PrimitiveRecord(int x, long y, double z) {
            this.x = x;
            this.y = y;
            this.z = z;
        }

        long sum() {
            return x + y + (long) z;
        }
    }

    public static final class ReferenceRecord {
        private Object value;

        ReferenceRecord(Object value) {
            this.value = value;
        }
    }

    public static class NonFinalRecord {
        private int x;

        NonFinalRecord(int x) {
            this.x = x;
        }
    }

    public static final class UnregisteredRecord {
        private int x;

        UnregisteredRecord(int x) {
            this.x = x;
        }
    }

    public static final class Holder {
        private Object value;
    }

    public static final class GenericCell<T> {
        private T value;

        GenericCell(T value) {
            this.value = value;
        }
    }

}
