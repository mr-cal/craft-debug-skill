fn main() {
    cc::Build::new().file("native/png_version.c").compile("png_version");
    println!("cargo:rustc-link-lib=png16");
    println!("cargo:rerun-if-changed=native/png_version.c");
}
