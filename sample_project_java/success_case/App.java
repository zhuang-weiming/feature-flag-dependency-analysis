package sample_project_java.success_case;

public class App {
    public static void foo() {
        if (FeatureFlag.isFeatureEnabled("flag_a")) {
            System.out.println("flag_a enabled in foo");
        }
    }

    public static void bar() {
        if (FeatureFlag.isFeatureEnabled("flag_b")) {
            System.out.println("flag_b enabled in bar");
        }
    }

    public static void baz() {
        if (FeatureFlag.isFeatureEnabled("flag_c")) {
            System.out.println("flag_c enabled in baz");
        }
    }

    public static void main(String[] args) {
        foo();
        bar();
        baz();
    }
}
