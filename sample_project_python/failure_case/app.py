# 有依赖用例：同一函数/调用链中出现多个feature flag，存在依赖
from feature_flag import is_feature_enabled

def foo():
    if is_feature_enabled("flag_a") and is_feature_enabled("flag_b"):
        print("flag_a and flag_b both enabled in foo")

def bar():
    if is_feature_enabled("flag_b"):
        print("flag_b enabled in bar")
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
