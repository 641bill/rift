import jdk.internal.rift.RiftRegion;

public final class RiftHotSpotSafepointProbe {
    private static final int OPEN = 1;
    private static final int USED = 4;
    private static final int OBJECT_ALLOCS = 12;

    public static void main(String[] args) throws Exception {
        if (args.length != 1) {
            throw new IllegalArgumentException("expected mode: safepoint or system-gc");
        }
        RiftRegion.registerEligible(PrimitiveRecord.class);
        if ("safepoint".equals(args[0])) {
            checkSafepointOnly();
            System.out.println("safepoint-probe-ok");
        } else if ("system-gc".equals(args[0])) {
            checkSystemGc();
            System.out.println("system-gc-probe-ok");
        } else {
            throw new IllegalArgumentException("unknown mode: " + args[0]);
        }
    }

    private static void checkSafepointOnly() throws Exception {
        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        PrimitiveRecord record = null;
        try {
            record = new PrimitiveRecord(1, 2L, 3.0d);
            check(record.sum() == 6L, "record checksum before safepoint");
            checkStats(handle, 1);
            RiftRegion.verifyLive(record);

            Thread.sleep(1L);

            RiftRegion.verifyLive(record);
            check(record.sum() == 6L, "record checksum after safepoint");
        } finally {
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }
        expectClosed(record);
    }

    private static void checkSystemGc() {
        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        PrimitiveRecord record = null;
        try {
            record = new PrimitiveRecord(4, 5L, 6.0d);
            check(record.sum() == 15L, "record checksum before gc");
            checkStats(handle, 1);
            RiftRegion.verifyLive(record);

            System.gc();

            RiftRegion.verifyLive(record);
            check(record.sum() == 15L, "record checksum after gc");
        } finally {
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }
        expectClosed(record);
    }

    private static void checkStats(long handle, long expectedObjects) {
        long[] stats = RiftRegion.stats(handle);
        check(stats[OPEN] == 1, "region should be open");
        check(stats[USED] > 0, "region should have used bytes");
        check(stats[OBJECT_ALLOCS] == expectedObjects, "region object count: " + stats[OBJECT_ALLOCS]);
    }

    private static void expectClosed(Object value) {
        try {
            RiftRegion.verifyLive(value);
            throw new AssertionError("closed region object should fail verifyLive");
        } catch (IllegalStateException expected) {
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
}
