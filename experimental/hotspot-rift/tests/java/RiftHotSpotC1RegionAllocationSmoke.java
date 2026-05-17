import jdk.internal.rift.RiftRegion;

public final class RiftHotSpotC1RegionAllocationSmoke {
    private static final int OPEN = 1;
    private static final int USED = 4;
    private static final int OBJECT_ALLOCS = 12;

    public static void main(String[] args) {
        RiftRegion.registerEligible(PrimitiveRecord.class);

        long warmup = 0;
        for (int i = 0; i < 20_000; i++) {
            warmup += allocateOne(i).sum();
        }
        check(warmup != 0, "warmup should execute");

        long handle = RiftRegion.open(1 << 20);
        long checksum = 0;
        RiftRegion.enter(handle);
        try {
            for (int i = 0; i < 10_000; i++) {
                PrimitiveRecord record = allocateOne(i);
                RiftRegion.verifyLive(record);
                checksum += record.sum();
            }

            long[] active = RiftRegion.stats(handle);
            check(active[OPEN] == 1, "region should be open");
            check(active[USED] > 0, "C1 allocation should use region bytes");
            check(active[OBJECT_ALLOCS] == 10_000, "C1 allocation count: " + active[OBJECT_ALLOCS]);
        } finally {
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }

        check(checksum == expected(10_000), "checksum: " + checksum);
        System.out.println("c1-allocation-ok");
    }

    private static PrimitiveRecord allocateOne(int i) {
        return new PrimitiveRecord(i, i + 1L, i + 2.0d);
    }

    private static long expected(int count) {
        long total = 0;
        for (int i = 0; i < count; i++) {
            total += i + (i + 1L) + (long) (i + 2.0d);
        }
        return total;
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
