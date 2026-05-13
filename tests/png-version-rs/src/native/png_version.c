#include <png.h>

unsigned long png_runtime_version(void)
{
    return png_access_version_number();
}
