use std::os::raw::c_ulong;

unsafe extern "C" {
    fn png_runtime_version() -> c_ulong;
}

fn main() {
    let version = unsafe { png_runtime_version() };
    println!("libpng runtime version: 0x{version:x}");
}
