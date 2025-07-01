public class Main {
    public static void main(String[] args) {
        paymentFlow();
        dashboard();
    }

    public static void paymentFlow() {
        if (FeatureFlag.isEnabled("new-payment-flow")) {
            System.out.println("Using new payment flow.");
            if (FeatureFlag.isEnabled("experimental-recommendations")) {
                System.out.println("Showing experimental recommendations.");
            }
        } else {
            System.out.println("Using old payment flow.");
        }
    }

    public static void dashboard() {
        if (FeatureFlag.isEnabled("beta-dashboard")) {
            System.out.println("Showing beta dashboard.");
        } else {
            System.out.println("Showing standard dashboard.");
        }
    }
}
