public class FeatureFlag {
    public static boolean isEnabled(String flagName) {
        // In a real application, this would check a feature flag service.
        // For this example, we'll just use a simple switch statement.
        switch (flagName) {
            case "new-payment-flow":
                return true;
            case "experimental-recommendations":
                return false;
            case "beta-dashboard":
                return true;
            default:
                return false;
        }
    }
}
