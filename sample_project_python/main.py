def is_feature_enabled(flag_name):
    # 假设所有flag都为True，仅用于演示
    return True

def foo():
    if is_feature_enabled("flag_a"):
        print("flag_a enabled in foo")
    if is_feature_enabled("flag_b"):
        print("flag_b enabled in foo")

def bar():
    if is_feature_enabled("flag_b"):
        print("flag_b enabled in bar")
    if is_feature_enabled("flag_c"):
        print("flag_c enabled in bar")
    foo()

def baz():
    if is_feature_enabled("flag_a") and is_feature_enabled("flag_c"):
        print("flag_a and flag_c both enabled in baz")
    bar()

def main():
    foo()
    bar()
    baz()

if __name__ == "__main__":
    main()
