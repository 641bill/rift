import jdk.internal.rift.RiftRegion;

public final class RiftHotSpotC1StoreGuardSmoke {
    private static Object escapedStatic;

    public static void main(String[] args) {
        RiftRegion.registerEligible(PrimitiveRecord.class);

        Object warm = new UnregisteredRecord(1);
        Holder holder = new Holder();
        Object[] array = new Object[1];
        for (int i = 0; i < 20_000; i++) {
            storeStatic(warm);
            storeField(holder, warm);
            storeArray(array, warm);
        }
        escapedStatic = null;
        holder.value = null;
        array[0] = null;

        long handle = RiftRegion.open(4096);
        RiftRegion.enter(handle);
        try {
            PrimitiveRecord record = new PrimitiveRecord(1, 2L, 3.0d);
            RiftRegion.verifyLive(record);
            try {
                storeStatic(record);
                throw new AssertionError("C1 putstatic should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
            try {
                storeField(new Holder(), record);
                throw new AssertionError("C1 putfield should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
            try {
                storeArray(new Object[1], record);
                throw new AssertionError("C1 aastore should fail");
            } catch (IllegalStateException expected) {
                // expected
            }
        } finally {
            escapedStatic = null;
            RiftRegion.leave(handle);
            RiftRegion.close(handle);
        }

        System.out.println("c1-store-guard-ok");
    }

    private static void storeStatic(Object value) {
        escapedStatic = value;
    }

    private static void storeField(Holder holder, Object value) {
        holder.value = value;
    }

    private static void storeArray(Object[] array, Object value) {
        array[0] = value;
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
}
