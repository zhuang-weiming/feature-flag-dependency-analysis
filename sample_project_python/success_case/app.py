# 无依赖用例：每个函数只用一个feature flag，互不影响
from feature_flag import is_feature_enabled

def foo():
    if is_feature_enabled("flag_a"):
        print("flag_a enabled in foo")

def bar():
    if is_feature_enabled("flag_b"):
        print("flag_b enabled in bar")

def baz():
    if is_feature_enabled("flag_c"):
        print("flag_c enabled in baz")

def main():
    foo()
    bar()
    baz()

if __name__ == "__main__":
    main()
