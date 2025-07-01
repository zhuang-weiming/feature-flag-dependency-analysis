package sample_project_java.failure_case;

public class App {
    public static void foo() {
        if (FeatureFlag.isFeatureEnabled("flag_a") && FeatureFlag.isFeatureEnabled("flag_b")) {
            System.out.println("flag_a and flag_b both enabled in foo");
        }
    }

    public static void bar() {
        if (FeatureFlag.isFeatureEnabled("flag_b")) {
            System.out.println("flag_b enabled in bar");
        }
        foo();
    }

    public static void baz() {
        if (FeatureFlag.isFeatureEnabled("flag_a") && FeatureFlag.isFeatureEnabled("flag_c")) {
            System.out.println("flag_a and flag_c both enabled in baz");
        }
        bar();
    }

    public static void main(String[] args) {
        foo();
        bar();
        baz();
    }
}
